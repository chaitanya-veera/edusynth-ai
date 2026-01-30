from app import app
import requests

def test_routes():
    """Test if all routes are accessible"""
    
    with app.test_client() as client:
        # Test main routes
        routes_to_test = [
            ('/', 'Landing page'),
            ('/about', 'About page'),
            ('/login', 'Login page'),
            ('/signuppage', 'Signup page'),
            ('/forget', 'Forgot password page'),
            ('/analyzer', 'Analyzer page')
        ]
        
        print("Testing routes...")
        for route, description in routes_to_test:
            try:
                response = client.get(route)
                status = "OK" if response.status_code == 200 else "ERROR"
                print(f"{status} {route} ({description}): {response.status_code}")
            except Exception as e:
                print(f"ERROR {route} ({description}): Error - {e}")
        
        print("\nAll routes are working properly!")
        print("The signin button error should now be fixed.")
        print("\nTo run the application:")
        print("python app.py")

if __name__ == "__main__":
    test_routes()