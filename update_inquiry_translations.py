# Update translations.js with proper inquiry translations

with open('projects/Cauchemar/js/translations.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if inquiry translations already exist
if '"inquiry"' not in content or 'section_client' not in content:
    print("⚠️  Need to add complete inquiry translations")
    
    # Korean inquiry section - replace the simple one with complete version
    new_ko_inquiry = '''        inquiry: {
            title: "비즈니스 문의",
            subtitle: "Cauchemar 크루와의 협업을 제안해주세요.",
            section_client: "클라이언트 정보",
            name: "이름 *",
            email: "이메일 *",
            company: "회사명",
            phone: "연락처",
            section_project: "프로젝트 정보",
            project_title: "프로젝트 제목 *",
            budget: "예산 범위",
            start_date: "프로젝트 시작 희망일",
            description: "프로젝트 상세 설명 *",
            description_placeholder: "프로젝트에 대해 자세히 알려주세요...",
            submit: "문의 제출"
        }'''
    
    # Find and replace Korean inquiry section
    import re
    content = re.sub(
        r'inquiry: \{[^}]+\}',
        new_ko_inquiry,
        content,
        flags=re.DOTALL
    )
    
    with open('projects/Cauchemar/js/translations.js', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated translations.js!")
else:
    print("✅ Translations already complete!")
