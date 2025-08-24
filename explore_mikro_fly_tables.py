#!/usr/bin/env python
"""
Mikro Fly V17 veritabanı yapısını keşfet
"""

import pyodbc
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def explore_mikro_fly_tables():
    """Mikro Fly tablolarını ve yapısını keşfet"""
    
    # Environment variables'dan bağlantı bilgilerini al
    server = os.getenv('MIKRO_FLY_SERVER', 'localhost')
    database = os.getenv('MIKRO_FLY_DATABASE', 'MikroFly_V17')
    username = os.getenv('MIKRO_FLY_USERNAME', 'sa')
    password = os.getenv('MIKRO_FLY_PASSWORD', '')
    
    # Bağlantı string'i oluştur - Windows Authentication
    if username.startswith('DOMAIN\\') or '\\' in username:
        conn_str = f"""
            DRIVER={{SQL Server}};
            SERVER={server};
            DATABASE={database};
            Trusted_Connection=yes;
        """
    else:
        conn_str = f"""
            DRIVER={{SQL Server}};
            SERVER={server};
            DATABASE={database};
            UID={username};
            PWD={password};
            Trusted_Connection=no;
        """
    
    try:
        print("Mikro Fly tablolari kesfedeiliyor...")
        
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Cari ile ilgili tabloları ara
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND (TABLE_NAME LIKE '%CARI%' OR TABLE_NAME LIKE '%MUSTERI%' OR TABLE_NAME LIKE '%CUSTOMER%')
                ORDER BY TABLE_NAME
            """)
            
            cari_tables = cursor.fetchall()
            print(f"\n=== CARI/MUSTERI TABLOLARI ({len(cari_tables)} adet) ===")
            for table in cari_tables:
                print(f"  - {table[0]}")
            
            # En muhtemel cari tablosunu bul ve yapisini incele
            if cari_tables:
                main_table = cari_tables[0][0]  # Ilk tabloyu al
                print(f"\n=== {main_table} TABLO YAPISI ===")
                
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{main_table}'
                    ORDER BY ORDINAL_POSITION
                """)
                
                columns = cursor.fetchall()
                for col in columns:
                    col_name, data_type, nullable, max_length = col
                    length_info = f"({max_length})" if max_length else ""
                    null_info = "NULL" if nullable == "YES" else "NOT NULL"
                    print(f"  {col_name:<30} {data_type}{length_info:<15} {null_info}")
                
                # Ornek veri kontrol et
                try:
                    cursor.execute(f"SELECT TOP 3 * FROM {main_table}")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        print(f"\n=== {main_table} ORNEK VERI ===")
                        print(f"Toplamda {len(sample_data)} ornek kayit bulundu")
                        # Ilk kaydin sadece ilk birkac alanini goster
                        if len(sample_data) > 0:
                            first_record = sample_data[0]
                            print(f"Ilk kayit: {str(first_record)[:100]}...")
                except Exception as e:
                    print(f"Ornek veri alinamadi: {e}")
            
            return True
            
    except Exception as e:
        print(f"HATA: {e}")
        return False

if __name__ == "__main__":
    explore_mikro_fly_tables()