# database.py - Complete database operations with vessel and manager management

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import pandas as pd


class VesselDatabase:
    def __init__(self):
        self.connection = None

    def create_connection(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error: {e}")
            return False

    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            temp_config = DB_CONFIG.copy()
            temp_config.pop('database', None)
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"Error creating database: {e}")
            return False

    # ========================================
    # VESSEL/MASTER DETAILS MANAGEMENT
    # ========================================

    def fix_vessel_table_schema(self):
        """Fix vessel table schema - migrate to correct structure"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            cursor = self.connection.cursor()

            # Check if table exists and get its structure
            try:
                cursor.execute("DESCRIBE vessel_details")
                columns = {row[0]: row[1] for row in cursor.fetchall()}

                # Check required columns
                required_columns = ['vessel_name', 'master_manager_email', 'contact_details']
                has_all = all(col in columns for col in required_columns)

                if has_all:
                    cursor.close()
                    return True, "✅ Vessel table schema is correct"

                print("⚠️ Incorrect vessel table schema detected. Starting migration...")

                # Backup existing data
                cursor.execute("SELECT * FROM vessel_details")
                old_data = cursor.fetchall()
                old_column_names = [desc[0] for desc in cursor.description]

                print(f"📦 Backing up {len(old_data)} existing records...")

            except mysql.connector.Error as err:
                if err.errno == 1146:  # Table doesn't exist
                    print("ℹ️ Vessel table doesn't exist. Will create new one.")
                    old_data = []
                    old_column_names = []
                else:
                    raise err

            # Drop old table
            cursor.execute("DROP TABLE IF EXISTS vessel_details")
            print("🗑️ Old vessel table dropped")

            # Create new table with correct schema
            create_table_query = """
                CREATE TABLE vessel_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    vessel_name VARCHAR(255) NOT NULL UNIQUE,
                    master_manager_email TEXT,
                    contact_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
            cursor.execute(create_table_query)
            print("✅ New vessel table created with correct schema")

            # Migrate old data
            if old_data and old_column_names:
                migrated = 0
                failed = 0

                for row in old_data:
                    try:
                        row_dict = dict(zip(old_column_names, row))

                        insert_query = """
                            INSERT INTO vessel_details (vessel_name, master_manager_email, contact_details, created_at)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            str(row_dict.get('vessel_name', '')).upper(),
                            str(row_dict.get('master_manager_email', '')).upper(),
                            str(row_dict.get('contact_details', '')).upper(),
                            row_dict.get('created_at')
                        ))
                        migrated += 1
                    except Exception as e:
                        print(f"⚠️ Failed to migrate row: {e}")
                        failed += 1
                        continue

                print(f"📊 Migration complete: {migrated} migrated, {failed} failed")
                message = f"✅ Migration successful! Migrated {migrated} records."
            else:
                message = "✅ Vessel table created successfully!"

            self.connection.commit()
            cursor.close()

            return True, message

        except Error as e:
            return False, f"❌ Migration error: {e}"
        finally:
            self.close_connection()

    def create_tables(self):
        """Create vessel_details table (legacy method for compatibility)"""
        try:
            if not self.create_connection():
                return False

            cursor = self.connection.cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS vessel_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    vessel_name VARCHAR(255) NOT NULL UNIQUE,
                    master_manager_email TEXT,
                    contact_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error creating table: {e}")
            return False
        finally:
            self.close_connection()

    def insert_vessel(self, vessel_name, master_manager_email, contact_details):
        """Insert new vessel details - ALL UPPERCASE"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            # Convert to uppercase
            vessel_name = str(vessel_name).upper().strip()
            master_manager_email = str(master_manager_email).upper().strip()
            contact_details = str(contact_details).upper().strip()

            # Validate required fields
            if not vessel_name or not master_manager_email or not contact_details:
                return False, "All fields are required!"

            cursor = self.connection.cursor()
            query = """
                INSERT INTO vessel_details (vessel_name, master_manager_email, contact_details)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (vessel_name, master_manager_email, contact_details))
            self.connection.commit()
            cursor.close()
            return True, "Vessel details saved successfully!"
        except mysql.connector.IntegrityError:
            return False, "Vessel name already exists!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    def insert_vessels_bulk(self, vessels_data):
        """Insert multiple vessels from a list - IMPROVED"""
        success_count = 0
        failed_records = []

        for idx, vessel in enumerate(vessels_data, 1):
            try:
                # Get values with multiple fallback keys (case-insensitive)
                vessel_name = (
                        vessel.get('VESSEL NAME') or
                        vessel.get('vessel_name') or
                        vessel.get('Vessel Name') or
                        vessel.get('vesselname') or
                        vessel.get('VesselName') or
                        ''
                ).strip()

                master_manager_email = (
                        vessel.get('MASTER MANAGER EMAIL') or
                        vessel.get('master_manager_email') or
                        vessel.get('Master Manager Email') or
                        vessel.get('masteremail') or
                        vessel.get('master email') or
                        vessel.get('email') or
                        ''
                ).strip()

                contact_details = (
                        vessel.get('CONTACT DETAILS') or
                        vessel.get('contact_details') or
                        vessel.get('Contact Details') or
                        vessel.get('contact') or
                        vessel.get('details') or
                        ''
                ).strip()

                # Skip if any field is empty
                if not vessel_name or not master_manager_email or not contact_details:
                    failed_records.append({
                        'row': idx,
                        'vessel_name': vessel_name or 'MISSING',
                        'reason': 'Missing required fields'
                    })
                    continue

                # Try to insert
                success, message = self.insert_vessel(
                    vessel_name,
                    master_manager_email,
                    contact_details
                )

                if success:
                    success_count += 1
                else:
                    failed_records.append({
                        'row': idx,
                        'vessel_name': vessel_name,
                        'reason': message
                    })

            except Exception as e:
                failed_records.append({
                    'row': idx,
                    'vessel_name': vessel.get('VESSEL NAME', 'Unknown'),
                    'reason': str(e)
                })

        return success_count, failed_records

    def get_all_vessels(self):
        """Retrieve all vessel details"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, vessel_name, master_manager_email, contact_details, created_at
                FROM vessel_details
                ORDER BY vessel_name
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def search_vessel(self, vessel_name):
        """Search vessel by name, email, or contact details"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, vessel_name, master_manager_email, contact_details, created_at
                FROM vessel_details
                WHERE UPPER(vessel_name) LIKE UPPER(%s)
                   OR UPPER(master_manager_email) LIKE UPPER(%s)
                   OR UPPER(contact_details) LIKE UPPER(%s)
                ORDER BY vessel_name
            """
            search_pattern = f"%{vessel_name}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def get_vessel_by_name(self, vessel_name):
        """Get exact vessel by name"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM vessel_details WHERE vessel_name = %s"
            cursor.execute(query, (vessel_name,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def get_vessel_by_id(self, vessel_id):
        """Get vessel by ID"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM vessel_details WHERE id = %s"
            cursor.execute(query, (vessel_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def update_vessel(self, vessel_id, vessel_name, master_manager_email, contact_details):
        """Update vessel details - ALL UPPERCASE"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            # Convert to uppercase
            vessel_name = str(vessel_name).upper().strip()
            master_manager_email = str(master_manager_email).upper().strip()
            contact_details = str(contact_details).upper().strip()

            # Validate required fields
            if not vessel_name or not master_manager_email or not contact_details:
                return False, "All fields are required!"

            cursor = self.connection.cursor()
            query = """
                UPDATE vessel_details
                SET vessel_name = %s,
                    master_manager_email = %s,
                    contact_details = %s
                WHERE id = %s
            """
            cursor.execute(query, (vessel_name, master_manager_email, contact_details, vessel_id))
            self.connection.commit()

            if cursor.rowcount == 0:
                cursor.close()
                return False, "Vessel not found!"

            cursor.close()
            return True, "Vessel details updated successfully!"
        except mysql.connector.IntegrityError:
            return False, "Vessel name already exists!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    def delete_vessel(self, vessel_id):
        """Delete vessel"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            cursor = self.connection.cursor()
            query = "DELETE FROM vessel_details WHERE id = %s"
            cursor.execute(query, (vessel_id,))
            self.connection.commit()

            if cursor.rowcount == 0:
                cursor.close()
                return False, "Vessel not found!"

            cursor.close()
            return True, "Vessel deleted successfully!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    # ========================================
    # MANAGER MANAGEMENT
    # ========================================

    def fix_manager_table_schema(self):
        """Fix manager table schema - migrate from old to new structure"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            cursor = self.connection.cursor()

            # Check if table exists and get its structure
            try:
                cursor.execute("DESCRIBE managers")
                columns = {row[0]: row[1] for row in cursor.fetchall()}

                # Check if we already have the correct schema
                if 'address_and_contact' in columns:
                    cursor.close()
                    return True, "✅ Manager table schema is correct"

                print("⚠️ Old manager table schema detected. Starting migration...")

                # Backup existing data if any
                cursor.execute("SELECT * FROM managers")
                old_data = cursor.fetchall()
                old_column_names = [desc[0] for desc in cursor.description]

                print(f"📦 Backing up {len(old_data)} existing records...")

            except mysql.connector.Error as err:
                if err.errno == 1146:  # Table doesn't exist
                    print("ℹ️ Manager table doesn't exist. Will create new one.")
                    old_data = []
                    old_column_names = []
                else:
                    raise err

            # Drop old table if it exists
            cursor.execute("DROP TABLE IF EXISTS managers")
            print("🗑️ Old manager table dropped")

            # Create new table with correct schema
            create_table_query = """
                CREATE TABLE managers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    email_id VARCHAR(500) NOT NULL UNIQUE,
                    address_and_contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
            cursor.execute(create_table_query)
            print("✅ New manager table created with correct schema")

            # Migrate old data to new schema (if any existed)
            if old_data and old_column_names:
                migrated = 0
                failed = 0

                for row in old_data:
                    try:
                        row_dict = dict(zip(old_column_names, row))

                        # Combine old columns into new address_and_contact field
                        address_parts = []

                        # Handle old 'address' column
                        if 'address' in row_dict and row_dict['address']:
                            address_parts.append(str(row_dict['address']))

                        # Handle old 'contact_number' column
                        if 'contact_number' in row_dict and row_dict['contact_number']:
                            address_parts.append(f"CONTACT: {row_dict['contact_number']}")

                        combined_address = '\n'.join(address_parts) if address_parts else ''

                        # Insert into new table
                        insert_query = """
                            INSERT INTO managers (company_name, email_id, address_and_contact, created_at)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            str(row_dict.get('company_name', '')).upper(),
                            str(row_dict.get('email_id', '')).upper(),
                            combined_address.upper(),
                            row_dict.get('created_at')
                        ))
                        migrated += 1

                    except Exception as e:
                        print(f"⚠️ Failed to migrate row: {e}")
                        failed += 1
                        continue

                print(f"📊 Migration complete: {migrated} migrated, {failed} failed")
                message = f"✅ Migration successful! Migrated {migrated} records to new schema."
            else:
                message = "✅ Manager table created successfully!"

            self.connection.commit()
            cursor.close()

            return True, message

        except Error as e:
            return False, f"❌ Migration error: {e}"
        finally:
            self.close_connection()

    def create_manager_table(self):
        """Create managers table with COMPANY NAME, EMAIL ID, and ADDRESS AND CONTACT"""
        try:
            if not self.create_connection():
                return False

            cursor = self.connection.cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS managers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    email_id VARCHAR(500) NOT NULL UNIQUE,
                    address_and_contact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error creating managers table: {e}")
            return False
        finally:
            self.close_connection()

    def insert_manager(self, company_name, email_id, address_and_contact):
        """Insert new manager details - ALL UPPERCASE"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            # Convert to uppercase
            company_name = str(company_name).upper().strip()
            email_id = str(email_id).upper().strip()
            address_and_contact = str(address_and_contact).upper().strip()

            # Validate required fields
            if not company_name or not email_id or not address_and_contact:
                return False, "All fields are required!"

            cursor = self.connection.cursor()
            query = """
                INSERT INTO managers (company_name, email_id, address_and_contact)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (company_name, email_id, address_and_contact))
            self.connection.commit()
            cursor.close()
            return True, "Manager details saved successfully!"
        except mysql.connector.IntegrityError:
            return False, "Email ID already exists!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    def insert_managers_bulk(self, managers_data):
        """Insert multiple managers from a list - IMPROVED"""
        success_count = 0
        failed_records = []

        for idx, manager in enumerate(managers_data, 1):
            try:
                # Get values with multiple fallback keys
                company_name = (
                        manager.get('COMPANY NAME') or
                        manager.get('company_name') or
                        manager.get('Company Name') or
                        ''
                ).strip()

                email_id = (
                        manager.get('EMAIL ID') or
                        manager.get('email_id') or
                        manager.get('Email ID') or
                        ''
                ).strip()

                address_and_contact = (
                        manager.get('ADDRESS AND CONTACT') or
                        manager.get('address_and_contact') or
                        manager.get('Address and Contact') or
                        ''
                ).strip()

                # Skip if any field is empty
                if not company_name or not email_id or not address_and_contact:
                    failed_records.append({
                        'row': idx,
                        'company_name': company_name or 'MISSING',
                        'email_id': email_id or 'MISSING',
                        'reason': 'Missing required fields'
                    })
                    continue

                # Try to insert
                success, message = self.insert_manager(
                    company_name,
                    email_id,
                    address_and_contact
                )

                if success:
                    success_count += 1
                else:
                    failed_records.append({
                        'row': idx,
                        'company_name': company_name,
                        'email_id': email_id,
                        'reason': message
                    })

            except Exception as e:
                failed_records.append({
                    'row': idx,
                    'company_name': manager.get('COMPANY NAME', 'Unknown'),
                    'email_id': manager.get('EMAIL ID', 'Unknown'),
                    'reason': str(e)
                })

        return success_count, failed_records

    def get_all_managers(self):
        """Retrieve all manager details"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, company_name, email_id, address_and_contact, created_at
                FROM managers
                ORDER BY company_name
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def search_manager(self, search_term):
        """Search manager by company name, email, or address"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, company_name, email_id, address_and_contact, created_at
                FROM managers
                WHERE UPPER(company_name) LIKE UPPER(%s)
                   OR UPPER(email_id) LIKE UPPER(%s)
                   OR UPPER(address_and_contact) LIKE UPPER(%s)
                ORDER BY company_name
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def get_manager_by_id(self, manager_id):
        """Get manager by ID"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM managers WHERE id = %s"
            cursor.execute(query, (manager_id,))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def update_manager(self, manager_id, company_name, email_id, address_and_contact):
        """Update manager details - ALL UPPERCASE"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            # Convert to uppercase
            company_name = str(company_name).upper().strip()
            email_id = str(email_id).upper().strip()
            address_and_contact = str(address_and_contact).upper().strip()

            # Validate required fields
            if not company_name or not email_id or not address_and_contact:
                return False, "All fields are required!"

            cursor = self.connection.cursor()
            query = """
                UPDATE managers
                SET company_name = %s,
                    email_id = %s,
                    address_and_contact = %s
                WHERE id = %s
            """
            cursor.execute(query, (company_name, email_id, address_and_contact, manager_id))
            self.connection.commit()

            if cursor.rowcount == 0:
                cursor.close()
                return False, "Manager not found!"

            cursor.close()
            return True, "Manager details updated successfully!"
        except mysql.connector.IntegrityError:
            return False, "Email ID already exists!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    def delete_manager(self, manager_id):
        """Delete manager"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            cursor = self.connection.cursor()
            query = "DELETE FROM managers WHERE id = %s"
            cursor.execute(query, (manager_id,))
            self.connection.commit()

            if cursor.rowcount == 0:
                cursor.close()
                return False, "Manager not found!"

            cursor.close()
            return True, "Manager deleted successfully!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    # ========================================
    # INVOICE MANAGEMENT
    # ========================================

    def create_invoice_table(self):
        """Create invoices table if it doesn't exist"""
        try:
            if not self.create_connection():
                return False

            cursor = self.connection.cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS invoices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    invoice_number VARCHAR(50) NOT NULL UNIQUE,
                    vessel_name VARCHAR(255) NOT NULL,
                    port_of_delivery VARCHAR(255),
                    invoice_type VARCHAR(100),
                    currency VARCHAR(10) DEFAULT 'USD',
                    total_amount DECIMAL(15, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100)
                )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error creating invoices table: {e}")
            return False
        finally:
            self.close_connection()

    def insert_invoice(self, invoice_number, vessel_name, port_of_delivery, invoice_type, currency, total_amount):
        """Insert new invoice record"""
        try:
            if not self.create_connection():
                return False, "Database connection failed"

            cursor = self.connection.cursor()
            query = """
                INSERT INTO invoices (invoice_number, vessel_name, port_of_delivery, invoice_type, currency, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (invoice_number, vessel_name, port_of_delivery, invoice_type, currency, total_amount))
            self.connection.commit()
            cursor.close()
            return True, "Invoice saved successfully!"
        except mysql.connector.IntegrityError:
            return False, "Invoice number already exists!"
        except Error as e:
            return False, f"Error: {e}"
        finally:
            self.close_connection()

    def get_last_invoice_number(self):
        """Get the last invoice number"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result['invoice_number'] if result else None
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()

    def get_all_invoices(self):
        """Retrieve all invoices"""
        try:
            if not self.create_connection():
                return None

            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT invoice_number,
                       vessel_name,
                       port_of_delivery,
                       invoice_type,
                       currency,
                       total_amount,
                       created_at
                FROM invoices
                ORDER BY id DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close_connection()


# ========================================
# INITIALIZATION FUNCTION
# ========================================

def initialize_database():
    """Initialize database and tables with auto-migration"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    db = VesselDatabase()

    # Create database
    print("\n1. Creating database...")
    db.create_database()

    # Fix/migrate vessel table schema
    print("2. Checking vessel table schema...")
    success, message = db.fix_vessel_table_schema()
    print(f"   {message}")

    # Fix/migrate manager table schema
    print("3. Checking manager table schema...")
    success, message = db.fix_manager_table_schema()
    print(f"   {message}")

    # Create invoice table
    print("4. Creating invoice table...")
    db.create_invoice_table()

    print("\n" + "=" * 60)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("=" * 60 + "\n")

    return db