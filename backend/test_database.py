"""
Test script for Day 21: Database Layer
Verifies that SQLAlchemy models and database work correctly.
"""

from database import SessionLocal, engine, Base
from models import Project, Page, Bubble
from datetime import datetime

def test_database():
    print("=" * 50)
    print("Testing Database Layer (Day 21)")
    print("=" * 50)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # 1. Create a test project
        print("\n[1/5] Creating test project...")
        project = Project(
            name="Test Comic - One Piece",
            description="Prueba de persistencia"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"[OK] Project created: {project.name} (ID: {project.id})")
        
        # 2. Create a test page
        print("\n[2/5] Creating test page...")
        page = Page(
            project_id=project.id,
            filename="test_page_001.jpg",
            original_url="/uploads/test_page_001.jpg",
            final_url="/uploads/final_test_page_001.jpg",
            status="completed",
            page_number=1
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        print(f"[OK] Page created: {page.filename} (ID: {page.id})")
        
        # 3. Create test bubbles
        print("\n[3/5] Creating test bubbles...")
        bubble1 = Bubble(
            page_id=page.id,
            bbox=[100, 100, 300, 200],
            original_text="Hello World!",
            translated_text="¡Hola Mundo!",
            font="ComicNeue",
            confidence=95,
            bubble_type="speech",
            translation_provider="Gemini Flash (AI)"
        )
        
        bubble2 = Bubble(
            page_id=page.id,
            bbox=[350, 150, 550, 250],
            original_text="BOOM!",
            translated_text="¡BUM!",
            font="WildWords",
            confidence=98,
            bubble_type="shout",
            translation_provider="Gemini Flash (AI)"
        )
        
        db.add_all([bubble1, bubble2])
        db.commit()
        print(f"[OK] Bubbles created: 2 total")
        
        # 4. Query and verify relationships
        print("\n[4/5] Testing relationships...")
        retrieved_project = db.query(Project).filter(Project.id == project.id).first()
        print(f"   Project: {retrieved_project.name}")
        print(f"   Pages: {len(retrieved_project.pages)}")
        
        retrieved_page = retrieved_project.pages[0]
        print(f"   Page filename: {retrieved_page.filename}")
        print(f"   Bubbles in page: {len(retrieved_page.bubbles)}")
        
        for idx, bubble in enumerate(retrieved_page.bubbles, 1):
            print(f"   Bubble {idx}: '{bubble.original_text}' -> '{bubble.translated_text}'")
        
        print("[OK] Relationships working correctly!")
        
        # 5. Cleanup (optional - remove test data)
        print("\n[5/5] Cleaning up test data...")
        db.delete(project)  # Cascade will delete pages and bubbles
        db.commit()
        print("[OK] Test data cleaned up")
        
        print("\n" + "=" * 50)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Database layer is working correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_database()

