#!/usr/bin/env python
"""
STOKLAR ve URUNLER tablolarını incele
"""

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def check_stoklar_urunler():
    server = os.getenv('MIKRO_FLY_SERVER', 'localhost')
    database = os.getenv('MIKRO_FLY_DATABASE', 'MikroFly_V17')
    username = os.getenv('MIKRO_FLY_USERNAME', 'sa')
    
    conn_str = f"""
        DRIVER={{SQL Server}};
        SERVER={server};
        DATABASE={database};
        Trusted_Connection=yes;
    """
    
    try:
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            
            # STOKLAR tablosunu incele
            print("=== STOKLAR TABLO YAPISI ===")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'STOKLAR'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                col_name, data_type, nullable, max_length = col
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  {col_name:<35} {data_type}{length_info:<15} {null_info}")
            
            # Kayıt sayısını kontrol et
            cursor.execute("SELECT COUNT(*) FROM STOKLAR")
            count = cursor.fetchone()[0]
            print(f"\n=== STOKLAR KAYIT SAYISI: {count} ===")
            
            # Örnek kayıtları incele
            cursor.execute("SELECT TOP 5 * FROM STOKLAR")
            sample_records = cursor.fetchall()
            
            if sample_records:
                print(f"\n=== STOKLAR ILKK 5 KAYIT (sadece bazi alanlar) ===")
                for i, record in enumerate(sample_records, 1):
                    # İlk birkaç alanı göster
                    print(f"Kayit {i}: {str(record)[:200]}...")
            
            print("\n" + "="*80)
            
            # URUNLER tablosunu incele
            print("=== URUNLER TABLO YAPISI ===")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'URUNLER'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                col_name, data_type, nullable, max_length = col
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  {col_name:<35} {data_type}{length_info:<15} {null_info}")
            
            # Kayıt sayısını kontrol et
            cursor.execute("SELECT COUNT(*) FROM URUNLER")
            count = cursor.fetchone()[0]
            print(f"\n=== URUNLER KAYIT SAYISI: {count} ===")
            
            # Örnek kayıtları incele
            cursor.execute("SELECT TOP 5 * FROM URUNLER")
            sample_records = cursor.fetchall()
            
            if sample_records:
                print(f"\n=== URUNLER ILKK 5 KAYIT (sadece bazi alanlar) ===")
                for i, record in enumerate(sample_records, 1):
                    # İlk birkaç alanı göster
                    print(f"Kayit {i}: {str(record)[:200]}...")
                    
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    check_stoklar_urunler()