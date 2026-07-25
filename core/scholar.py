import requests
import re

# dashboard.py ile tam uyumlu olması için limit kelimesini max_results yaptık
def search_papers(query, max_results=10): 
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "resultType": "core", 
        "pageSize": 30
    }
    
    try:
        response = requests.get(url, params=params, timeout=15) 
        if response.status_code == 200:
            data = response.json().get("resultList", {}).get("result", [])
            valid_papers = []
            
            for p in data:
                abstract = p.get('abstractText')
                if abstract and len(abstract) > 30:
                    # Eski bozuk replace() komutları yerine, metinleri HTML etiketlerinden temizleyen sağlam kod
                    clean_abstract = re.sub(r'<[^>]+>', '', abstract)
                    
                    # KATMAN 8: Atıf Sayısı ve Dergi İsmini Çekiyoruz
                    journal_info = p.get('journalInfo', {})
                    journal = journal_info.get('journal', {}).get('title', 'Bilinmeyen Dergi')
                    citations = p.get('citedByCount', 0)
                    
                    valid_papers.append({
                        "title": p.get("title", "Başlıksız"),
                        "year": p.get("pubYear", "Tarihsiz"),
                        "authors": [{"name": p.get("authorString", "Bilinmeyen Yazar")}],
                        "abstract": clean_abstract,
                        "journal": journal,
                        "citations": citations
                    })
            return valid_papers[:max_results]
        else:
            return []
    except Exception as e:
         print(f"Hata detayı: {e}")
         return []
