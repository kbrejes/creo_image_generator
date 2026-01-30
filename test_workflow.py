#!/usr/bin/env python3
"""Test script for Ad Creative API endpoints."""

import requests
import json
import time

BASE_URL = "https://creo.yourads.io"

def test_generate_copy():
    """Test copy generation endpoint (if it exists)."""
    print("\n" + "="*50)
    print("TEST 1: Copy Generation")
    print("="*50)
    # This would be done in Dify via LLM, skipping
    print("✓ Copy generation handled by Dify LLM nodes")

def test_image_generation():
    """Test image generation endpoint."""
    print("\n" + "="*50)
    print("TEST 2: Image Generation")
    print("="*50)

    payload = {
        "prompt": "A young person with glasses looking excited and pointing at camera, bright yellow background, photo realistic, professional lighting",
        "backend": "flux",
        "aspect_ratio": "1:1"
    }

    print(f"Request: POST {BASE_URL}/tools/generate-image")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/tools/generate-image",
            json=payload,
            timeout=60
        )

        print(f"\nStatus: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("success") and result.get("images"):
            print(f"\n✓ Image generated: {result['images'][0]['url']}")
            return result['images'][0]['url']
        else:
            print(f"\n✗ Failed: {result.get('error', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

def test_compose_ad(image_url=None):
    """Test ad composition with text overlay."""
    print("\n" + "="*50)
    print("TEST 3: Text Overlay Composition")
    print("="*50)

    if not image_url:
        # Use a test image URL
        image_url = "https://creo.yourads.io/files/generated/test.png"

    params = {
        "image_url": image_url,
        "hook_text": "CHECK THIS OUT!",
        "body_text": "",
        "cta_text": "Learn More",
        "output_size": "instagram_square",
        "hook_font_size": 120,
        "body_font_size": 60,
        "cta_font_size": 48
    }

    print(f"Request: POST {BASE_URL}/tools/compose-ad")
    print(f"Params: {json.dumps(params, indent=2)}")

    try:
        response = requests.post(
            f"{BASE_URL}/tools/compose-ad",
            params=params,
            timeout=30
        )

        print(f"\nStatus: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("success"):
            print(f"\n✓ Composed image: {result.get('url')}")
            return result.get('url')
        else:
            print(f"\n✗ Failed: {result.get('error', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None

def test_font_sizes():
    """Test different font sizes."""
    print("\n" + "="*50)
    print("TEST 4: Font Size Variations")
    print("="*50)

    test_image = "https://via.placeholder.com/1080x1080/4A90E2/ffffff"

    sizes = [
        {"hook": 80, "cta": 40, "label": "Small"},
        {"hook": 120, "cta": 48, "label": "Default"},
        {"hook": 160, "cta": 64, "label": "Large"},
    ]

    results = []
    for size in sizes:
        print(f"\nTesting {size['label']}: hook={size['hook']}pt, cta={size['cta']}pt")

        params = {
            "image_url": test_image,
            "hook_text": "TEST TEXT",
            "cta_text": "Click Here",
            "hook_font_size": size['hook'],
            "cta_font_size": size['cta'],
            "output_size": "instagram_square"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/tools/compose-ad",
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"  ✓ Generated: {result.get('url')}")
                    results.append({
                        "size": size['label'],
                        "url": result.get('url'),
                        "success": True
                    })
                else:
                    print(f"  ✗ Failed: {result.get('error')}")
                    results.append({"size": size['label'], "success": False})
            else:
                print(f"  ✗ HTTP {response.status_code}")
                results.append({"size": size['label'], "success": False})

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({"size": size['label'], "success": False})

    successful = sum(1 for r in results if r.get("success"))
    print(f"\n{successful}/{len(results)} font size tests passed")
    return results

def test_full_pipeline():
    """Test the complete pipeline."""
    print("\n" + "="*50)
    print("TEST 5: Full Pipeline")
    print("="*50)

    # Step 1: Generate image
    print("\nStep 1: Generating image...")
    image_url = test_image_generation()

    if not image_url:
        print("✗ Pipeline failed: Could not generate image")
        return False

    # Wait a bit
    time.sleep(2)

    # Step 2: Compose with text
    print("\nStep 2: Adding text overlay...")
    final_url = test_compose_ad(image_url)

    if not final_url:
        print("✗ Pipeline failed: Could not compose ad")
        return False

    print("\n" + "="*50)
    print("✓ FULL PIPELINE SUCCESS")
    print("="*50)
    print(f"Raw image: {image_url}")
    print(f"Final ad: {final_url}")
    return True

def test_api_health():
    """Test API health."""
    print("\n" + "="*50)
    print("TEST 0: API Health Check")
    print("="*50)

    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        result = response.json()

        print(f"Status: {response.status_code}")
        print(f"Name: {result.get('name')}")
        print(f"Version: {result.get('version')}")
        print(f"Status: {result.get('status')}")
        print(f"Image backends: {result.get('available_backends', {}).get('image', [])}")

        if result.get('status') == 'running':
            print("\n✓ API is healthy")
            return True
        else:
            print("\n✗ API unhealthy")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print(" AD CREATIVE API TEST SUITE")
    print("="*60)

    # Test 0: Health check
    if not test_api_health():
        print("\n❌ API is not accessible. Exiting.")
        return

    # Test 1: Copy (skip - handled by Dify)
    test_generate_copy()

    # Test 2: Image generation
    test_image_generation()

    # Test 3: Text composition
    test_compose_ad()

    # Test 4: Font sizes
    test_font_sizes()

    # Test 5: Full pipeline
    test_full_pipeline()

    print("\n" + "="*60)
    print(" TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
