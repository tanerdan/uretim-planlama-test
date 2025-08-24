#!/usr/bin/env python
"""
Mikro Fly V17 ürün/stok tablolarını keşfet
"""

import pyodbc
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def explore_mikro_fly_products():
    """Mikro Fly ürün/stok tablolarını keşfet"""
    
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
        print("Mikro Fly urun/stok tablolari kesfedeiliyor...")
        
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Stok ile ilgili tabloları ara
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND (TABLE_NAME LIKE '%STOK%' OR TABLE_NAME LIKE '%URUN%' OR TABLE_NAME LIKE '%MALZEME%' OR TABLE_NAME LIKE '%ITEM%')
                ORDER BY TABLE_NAME
            """)
            
            stok_tables = cursor.fetchall()
            print(f"\n=== STOK/URUN TABLOLARI ({len(stok_tables)} adet) ===")
            for table in stok_tables:
                print(f"  - {table[0]}")
            
            # En muhtemel stok tablosunu bul ve yapısını incele
            if stok_tables:
                main_table = stok_tables[0][0]  # İlk tabloyu al
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
                
                # Kayıt sayısını kontrol et
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                    count = cursor.fetchone()[0]
                    print(f"\n=== {main_table} KAYIT SAYISI: {count} ===")
                except Exception as e:
                    print(f"Kayit sayisi alinamadi: {e}")
                
                # Örnek veri kontrol et
                try:
                    cursor.execute(f"SELECT TOP 3 * FROM {main_table}")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        print(f"\n=== {main_table} ORNEK VERI ===")
                        print(f"Toplamda {len(sample_data)} ornek kayit bulundu")
                        # İlk kayıtın sadece ilk birkaç alanını göster
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
    explore_mikro_fly_products()