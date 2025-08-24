#!/usr/bin/env python3
"""
Test script for selective TTS functionality with multi-language support.
Demonstrates how the system now only speaks for meaningful gestures in multiple languages.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tts_service import tts_service, LANGUAGE_MAPPINGS, IDLE_GESTURES

async def test_selective_tts():
    """Test the selective TTS functionality."""
    print("🎯 Testing Selective TTS Functionality")
    print("=" * 50)
    
    # Test meaningful gestures in different languages
    print("\n✅ Testing MEANINGFUL gestures in multiple languages:")
    meaningful_gestures = ["Class 0", "Class 1", "Class 2", "Class 3"]
    
    for gesture in meaningful_gestures:
        print(f"\nTesting gesture: {gesture}")
        
        # Test in English
        result_en = await tts_service.speak_gesture(gesture, language="en")
        print(f"  English: {result_en}")
        
        # Test in Vietnamese
        result_vn = await tts_service.speak_gesture(gesture, language="vn")
        print(f"  Vietnamese: {result_vn}")
        
        # Test in French
        result_fr = await tts_service.speak_gesture(gesture, language="fr")
        print(f"  French: {result_fr}")
    
    # Test idle gestures (should NOT speak in any language)
    print("\n⏭️  Testing IDLE gestures (should NOT trigger TTS in any language):")
    idle_gestures = ["hand_resting", "basic_movement", "none", "unknown"]
    
    for gesture in idle_gestures:
        print(f"\nTesting gesture: {gesture}")
        result = await tts_service.speak_gesture(gesture)
        print(f"  Result: {result}")
        
        if result["status"] == "skipped":
            print(f"  ✅ TTS correctly skipped: {result['reason']}")
        else:
            print(f"  ❌ TTS should have been skipped but wasn't")
    
    # Test edge cases
    print("\n🔍 Testing edge cases:")
    edge_cases = ["", "   ", "Class 99", "random_text"]
    
    for gesture in edge_cases:
        print(f"\nTesting gesture: '{gesture}'")
        result = await tts_service.speak_gesture(gesture)
        print(f"  Result: {result}")

def test_gesture_filtering():
    """Test the gesture filtering logic."""
    print("\n🧠 Testing Gesture Filtering Logic")
    print("=" * 50)
    
    test_gestures = [
        ("Class 0", "Hello", True),
        ("Class 1", "Yes", True),
        ("Class 99", "Unknown", False),
        ("hand_resting", "Rest", False),
        ("basic_movement", "Movement", False),
        ("", "Empty", False),
        ("   ", "Whitespace", False),
    ]
    
    for gesture, description, should_speak in test_gestures:
        result = tts_service.should_speak_gesture(gesture)
        status = "✅ SPEAK" if result else "⏭️  SKIP"
        print(f"{gesture:15} ({description:10}) -> {status}")
        
        if result != should_speak:
            print(f"  ⚠️  Expected: {'SPEAK' if should_speak else 'SKIP'}, Got: {'SPEAK' if result else 'SKIP'}")

def test_language_functionality():
    """Test the multi-language functionality."""
    print("\n🌍 Testing Multi-Language Functionality")
    print("=" * 50)
    
    # Test available languages
    available_languages = tts_service.get_available_languages()
    print(f"Available languages: {available_languages}")
    
    # Test current language
    print(f"Current language: {tts_service.current_language}")
    
    # Test language switching
    print("\nTesting language switching:")
    for language in available_languages:
        success = tts_service.set_language(language)
        print(f"  Set to {language}: {'✅ Success' if success else '❌ Failed'}")
        print(f"  Current language: {tts_service.current_language}")
    
    # Reset to English
    tts_service.set_language("en")
    print(f"  Reset to English: {tts_service.current_language}")
    
    # Test gesture text in different languages
    print("\nTesting gesture text in different languages:")
    test_gesture = "Class 0"
    for language in available_languages:
        text = tts_service.get_gesture_text(test_gesture, language)
        print(f"  {language}: '{text}'")

def test_ai_model_integration():
    """Test how the TTS system works with AI model predictions."""
    print("\n🤖 Testing AI Model Integration")
    print("=" * 50)
    
    print("This demonstrates how your AI model and TTS work together:")
    print()
    
    # Simulate AI model predictions
    ai_predictions = [
        {"gesture": "Class 0", "confidence": 0.95, "source": "AI Model"},
        {"gesture": "Class 1", "confidence": 0.87, "source": "AI Model"},
        {"gesture": "hand_resting", "confidence": 0.92, "source": "AI Model"},
        {"gesture": "Class 2", "confidence": 0.78, "source": "AI Model"},
    ]
    
    for prediction in ai_predictions:
        gesture = prediction["gesture"]
        confidence = prediction["confidence"]
        source = prediction["source"]
        
        print(f"🤖 {source} predicts: '{gesture}' (confidence: {confidence:.2f})")
        
        # TTS system decides whether to speak
        should_speak = tts_service.should_speak_gesture(gesture)
        
        if should_speak:
            # Get text in current language
            text = tts_service.get_gesture_text(gesture)
            print(f"  🎯 TTS: Will speak '{text}' (meaningful gesture)")
        else:
            print(f"  ⏭️  TTS: Silent (idle gesture)")
        
        print()

if __name__ == "__main__":
    print("🚀 Starting Selective TTS Tests with Multi-Language Support...")
    
    # Test gesture filtering logic
    test_gesture_filtering()
    
    # Test multi-language functionality
    test_language_functionality()
    
    # Test AI model integration
    test_ai_model_integration()
    
    # Test actual TTS functionality
    try:
        asyncio.run(test_selective_tts())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
    
    print("\n✨ Test script completed!")
    print("\n🎯 Key Points:")
    print("  ✅ Your AI model still does ALL the gesture recognition")
    print("  ✅ TTS system only decides WHEN to speak")
    print("  ✅ Multi-language support for English, Vietnamese, French")
    print("  ✅ Smart filtering prevents unnecessary speech")
    print("  ✅ Easy to add more languages and gestures") 