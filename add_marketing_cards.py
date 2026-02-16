# Add marketing cards to cauchemar.html
with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the closing </div> after World Construction
marker = '                </div>\n            </div>\n        </div>\n    </section>'

if marker in content:
    # Insert the two new cards before the closing divs
    new_cards = '''                </div>
                <!-- SNS 마케팅 (NEW) -->
                <div class="bg-glass p-8 rounded-3xl space-y-6 border border-purple-500/30">
                    <div class="text-4xl">📱</div>
                    <h3 class="text-2xl font-bold">SNS Marketing</h3>
                    <p class="text-gray-400">Instagram, 틱톡, YouTube 등 주요 SNS 채널을 통해 제페토 작품을 홍보하고 바이럴 마케팅을 진행합니다.</p>
                    <ul class="text-sm text-gray-500 space-y-2">
                        <li>• Instagram 피드 + 스토리</li>
                        <li>• 틱톡 쇼츠 및 챌린지</li>
                        <li>• 해시태그 최적화 전략</li>
                    </ul>
                </div>
                <!-- 브랜드 협업 (NEW) -->
                <div class="bg-glass p-8 rounded-3xl space-y-6 border border-purple-500/30">
                    <div class="text-4xl">🤝</div>
                    <h3 class="text-2xl font-bold">Brand Partnership</h3>
                    <p class="text-gray-400">제페토 공식 브랜드와의 파트너십 연결 및 인플루언서 협업을 통한 전문 마케팅 서비스를 제공합니다.</p>
                    <ul class="text-sm text-gray-500 space-y-2">
                        <li>• 브랜드 매칭 및 제안서 작성</li>
                        <li>• 인플루언서 크리에이터 섭외</li>
                        <li>• 이벤트 기획 및 캠페인 운영</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>'''
    
    content = content.replace(marker, new_cards)
    
    with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added SNS Marketing and Brand Partnership cards!")
else:
    print("❌ Marker not found")
