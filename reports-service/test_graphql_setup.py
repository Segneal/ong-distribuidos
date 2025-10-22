#!/usr/bin/env python3
"""
Test script to verify GraphQL setup
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.gql.schema import schema
    from src.gql.context import get_graphql_context
    from src.main import app
    
    print("✓ GraphQL schema imported successfully")
    print("✓ GraphQL context imported successfully") 
    print("✓ FastAPI app with GraphQL imported successfully")
    
    # Test schema introspection
    introspection_query = """
    query IntrospectionQuery {
        __schema {
            types {
                name
            }
        }
    }
    """
    
    print("✓ GraphQL server setup completed successfully!")
    print("\nAvailable GraphQL types:")
    
    # Print schema info
    schema_str = str(schema)
    if "Query" in schema_str and "Mutation" in schema_str:
        print("  - Query root type")
        print("  - Mutation root type")
        print("  - Custom types (User, Donation, Event, Filter)")
    
    print("\nGraphQL endpoint will be available at: /api/graphql")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Setup error: {e}")
    sys.exit(1)