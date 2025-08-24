#!/usr/bin/env python
"""
Döviz kuru servisi - Oanda API kullanarak güncel kurları alır
"""

import requests
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
import json

logger = logging.getLogger(__name__)

class CurrencyService:
    """Döviz kuru servisi"""
    
    # Oanda API (gerçek API key gerekir)
    OANDA_BASE_URL = "https://api.exchangerate-api.com/v4/latest"  # Ücretsiz alternatif
    
    # Cache süresi (1 saat)
    CACHE_TIMEOUT = 3600
    
    # Desteklenen para birimleri
    SUPPORTED_CURRENCIES = [
        'USD', 'EUR', 'GBP', 'TRY', 'JPY', 'CHF', 'CAD', 'AUD'
    ]
    
    @classmethod
    def get_exchange_rates(cls, base_currency='USD'):
        """
        Verilen temel para birimi için tüm kurları al
        """
        cache_key = f"exchange_rates_{base_currency}"
        
        # Cache'den kontrol et
        rates = cache.get(cache_key)
        if rates:
            logger.info(f"Exchange rates loaded from cache for {base_currency}")
            return rates
        
        try:
            # API'den kur bilgilerini al
            rates = cls._fetch_from_api(base_currency)
            
            if rates:
                # Cache'e kaydet
                cache.set(cache_key, rates, cls.CACHE_TIMEOUT)
                logger.info(f"Exchange rates fetched and cached for {base_currency}")
                return rates
            else:
                # API'den alamazsa fallback kurları kullan
                logger.warning(f"Could not fetch rates from API, using fallback for {base_currency}")
                return cls._get_fallback_rates(base_currency)
                
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")
            return cls._get_fallback_rates(base_currency)
    
    @classmethod
    def _fetch_from_api(cls, base_currency):
        """API'den kur bilgilerini çek"""
        try:
            url = f"{cls.OANDA_BASE_URL}/{base_currency}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Sadece desteklenen para birimlerini al
                filtered_rates = {
                    currency: float(rate) 
                    for currency, rate in rates.items() 
                    if currency in cls.SUPPORTED_CURRENCIES
                }
                
                # Temel para birimini ekle
                filtered_rates[base_currency] = 1.0
                
                return {
                    'rates': filtered_rates,
                    'timestamp': datetime.now().isoformat(),
                    'base': base_currency,
                    'source': 'API'
                }
            else:
                logger.error(f"API request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return None
    
    @classmethod
    def _get_fallback_rates(cls, base_currency='USD'):
        """API erişimi olmadığında kullanılacak fallback kurlar"""
        
        # Sabit kurlar (güncellenebilir)
        fallback_rates = {
            'USD': {
                'USD': 1.0,
                'EUR': 0.85,
                'GBP': 0.73,
                'TRY': 27.50,
                'JPY': 110.0,
                'CHF': 0.92,
                'CAD': 1.25,
                'AUD': 1.45,
            }
        }
        
        if base_currency == 'USD':
            rates = fallback_rates['USD']
        else:
            # Diğer para birimleri için USD üzerinden hesapla
            usd_rates = fallback_rates['USD']
            base_to_usd = usd_rates.get(base_currency, 1.0)
            
            rates = {}
            for currency, usd_rate in usd_rates.items():
                if currency == base_currency:
                    rates[currency] = 1.0
                else:
                    rates[currency] = usd_rate / base_to_usd
        
        return {
            'rates': rates,
            'timestamp': datetime.now().isoformat(),
            'base': base_currency,
            'source': 'fallback'
        }
    
    @classmethod
    def convert_to_usd(cls, amount, from_currency):
        """
        Verilen miktarı USD'ye çevir
        
        Args:
            amount (Decimal): Çevrilecek miktar
            from_currency (str): Kaynak para birimi
        
        Returns:
            dict: {
                'usd_amount': Decimal('...'),
                'rate': Decimal('...'),
                'source': 'API' or 'fallback'
            }
        """
        if from_currency == 'USD':
            return {
                'usd_amount': amount,
                'rate': Decimal('1.0'),
                'source': 'direct'
            }
        
        # Kurları al (USD temel para birimi olarak)
        rates_data = cls.get_exchange_rates('USD')
        
        if from_currency in rates_data['rates']:
            # 1 USD = X from_currency
            # Yani 1 from_currency = (1/X) USD
            usd_per_unit = Decimal('1') / Decimal(str(rates_data['rates'][from_currency]))
            usd_amount = amount * usd_per_unit
            
            return {
                'usd_amount': usd_amount,
                'rate': usd_per_unit,
                'source': rates_data['source']
            }
        else:
            logger.error(f"Currency {from_currency} not supported")
            return {
                'usd_amount': amount,  # Fallback - aynı değer
                'rate': Decimal('1.0'),
                'source': 'error'
            }
    
    @classmethod
    def get_rate_to_usd(cls, from_currency):
        """
        Verilen para biriminin USD karşısındaki kurunu al
        
        Returns:
            Decimal: 1 from_currency = X USD
        """
        result = cls.convert_to_usd(Decimal('1.0'), from_currency)
        return result['rate']


# Örnek kullanım
if __name__ == "__main__":
    # Test
    service = CurrencyService()
    
    # Tüm kurları al
    rates = service.get_exchange_rates('USD')
    print("Exchange rates:", rates)
    
    # 100 EUR'yu USD'ye çevir
    result = service.convert_to_usd(Decimal('100'), 'EUR')
    print(f"100 EUR = {result['usd_amount']} USD (rate: {result['rate']})")