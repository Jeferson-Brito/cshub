"""
Script para gerar uma SECRET_KEY segura para Django
Execute: python generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*60)
    print("SUA SECRET_KEY:")
    print("="*60)
    print(secret_key)
    print("="*60)
    print("\nCopie este valor e use como SECRET_KEY no Render.\n")

