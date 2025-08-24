#!/usr/bin/env python
"""
Mikro Fly V17 bağlantısını test etmek için script
"""

import pyodbc
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def test_mikro_fly_connection():
    """Mikro Fly veritabanı bağlantısını test et"""
    
    # Environment variables'dan bağlantı bilgilerini al
    server = os.getenv('MIKRO_FLY_SERVER', 'localhost')
    database = os.getenv('MIKRO_FLY_DATABASE', 'MikroFly_V17')
    username = os.getenv('MIKRO_FLY_USERNAME', 'sa')
    password = os.getenv('MIKRO_FLY_PASSWORD', '')
    
    # Bağlantı string'i oluştur
    if username.startswith('DOMAIN\\') or '\\' in username:
        # Windows Authentication kullan
        conn_str = f"""
            DRIVER={{SQL Server}};
            SERVER={server};
            DATABASE={database};
            Trusted_Connection=yes;
        """
        print("Windows Authentication kullaniliyor...")
    else:
        # SQL Server Authentication kullan
        conn_str = f"""
            DRIVER={{SQL Server}};
            SERVER={server};
            DATABASE={database};
            UID={username};
            PWD={password};
            Trusted_Connection=no;
        """
        print("SQL Server Authentication kullaniliyor...")
    
    try:
        print("Mikro Fly V17 baglantisi test ediliyor...")
        print(f"Server: {server}")
        print(f"Database: {database}")
        print(f"Username: {username}")
        
        # Bağlantıyı dene
        with pyodbc.connect(conn_str, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Test sorgusu - veritabanı tabloları
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            tables = cursor.fetchall()
            print(f"BASARILI! {len(tables)} tablo bulundu.")
            
            # Cari hesap tablosunu kontrol et
            cursor.execute("""
                SELECT COUNT(*) as customer_count
                FROM CARI_HESAPLAR 
                WHERE cari_iptal = 0
            """)
            
            result = cursor.fetchone()
            customer_count = result[0] if result else 0
            print(f"Mikro Fly'de {customer_count} musteri kaydi bulundu.")
            
            return True
            
    except pyodbc.Error as e:
        print(f"HATA - Veritabani baglanti hatasi: {e}")
        print("\nKontrol edilecek noktalar:")
        print("   1. SQL Server servisi calisiyor mu?")
        print("   2. Veritabani adi dogru mu?")
        print("   3. Kullanici adi ve sifre dogru mu?")
        print("   4. SQL Server Mixed Mode authentication aktif mi?")
        return False
        
    except Exception as e:
        print(f"HATA - Genel hata: {e}")
        return False

if __name__ == "__main__":
    success = test_mikro_fly_connection()
    
    if success:
        print("\nMikro Fly baglantisi hazir! Artik senkronizasyon yapabilirsiniz.")
    else:
        print("\nBaglanti ayarlarini kontrol edip tekrar deneyin.")