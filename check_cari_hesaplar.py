#!/usr/bin/env python
"""
CARI_HESAPLAR tablosunu incele
"""

import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def check_cari_hesaplar():
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
            
            # CARI_HESAPLAR tablosunun yapisini incele
            print("=== CARI_HESAPLAR TABLO YAPISI ===")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'CARI_HESAPLAR'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                col_name, data_type, nullable, max_length = col
                length_info = f"({max_length})" if max_length else ""
                null_info = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  {col_name:<35} {data_type}{length_info:<15} {null_info}")
            
            # Kayit sayisini kontrol et
            cursor.execute("SELECT COUNT(*) FROM CARI_HESAPLAR")
            count = cursor.fetchone()[0]
            print(f"\n=== CARI_HESAPLAR KAYIT SAYISI: {count} ===")
            
            # Ornek kayitlari incele
            cursor.execute("SELECT TOP 5 * FROM CARI_HESAPLAR")
            sample_records = cursor.fetchall()
            
            if sample_records:
                print(f"\n=== ILKK 5 KAYIT (sadece bazi alanlar) ===")
                for i, record in enumerate(sample_records, 1):
                    # Ilk birkac alani goster
                    print(f"Kayit {i}: {str(record)[:150]}...")
            
            # Musteri tipindeki kayitlari bul
            print(f"\n=== MUSTERI TIPI KAYITLAR ===")
            
            # Muhtemel musteri kolon isimlerini test et
            test_queries = [
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_CariTip = 0",
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_CariTip = 1", 
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_CariTip = 2",
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_tip = 'M'",
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_tip = 'S'",
                "SELECT COUNT(*) FROM CARI_HESAPLAR WHERE cari_musteri_turu = 1"
            ]
            
            for query in test_queries:
                try:
                    cursor.execute(query)
                    result = cursor.fetchone()[0]
                    print(f"  {query} -> {result} kayit")
                except Exception as e:
                    print(f"  {query} -> HATA: {str(e)[:50]}...")
                    
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    check_cari_hesaplar()