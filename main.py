# test_supabase.py
# Run this script to test your Supabase connection
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def test_supabase_connection():
    # Replace with your actual Supabase credentials
    SUPABASE_URL = "https://rtkehbagrwajvhhvcuky.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0a2VoYmFncndhanZoaHZjdWt5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgyMDQwNTUsImV4cCI6MjA2Mzc4MDA1NX0.UKC4_OmDlGnTGDmJLR52Gk5Gp9uf7XISfYKU152jZhQ"

    print(f"Testing connection to: {SUPABASE_URL}")
    print(f"Using key: {SUPABASE_KEY[:20]}...")

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client created successfully")

        # Test table access
        response = supabase.table('user_profiles').select("count", count="exact").execute()
        print(f"✅ Successfully connected to user_profiles table")
        print(f"Current record count: {response.count}")

        # Test insert
        test_data = {
            'name': 'Test User',
            'email': 'ayusharya11oct@gmail.com',
            'is_verified': False
        }

        print("Testing insert...")
        insert_response = supabase.table('user_profiles').insert(test_data).execute()

        if insert_response.data:
            print("✅ Test insert successful")

            # Clean up - delete the test record
            # supabase.table('user_profiles').delete().eq('email', 'test@example.com').execute()
            print("✅ Test record cleaned up")
        else:
            print("❌ Test insert failed")
            print(f"Response: {insert_response}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_supabase_connection()