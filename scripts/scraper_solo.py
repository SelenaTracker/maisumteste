#!/usr/bin/env python3
"""
Scraper para Selena Gomez Solo - Kworb.net
Atualiza: https://kworb.net/spotify/artist/0C8ZW7ezQVs4URX5aX7Kqx_songs.html
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz

def get_brazil_time():
    """Retorna data/hora atual no horário de Brasília"""
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %z')

def parse_streams(streams_text):
    """Converte texto como '1.43B', '905M', '265K' para número inteiro"""
    if not streams_text or streams_text == '-':
        return 0
    
    streams_text = streams_text.strip().upper()
    
    # Remover vírgulas e caracteres especiais
    streams_text = streams_text.replace(',', '').replace(' ', '')
    
    multipliers = {
        'B': 1000000000,  # Bilhões
        'M': 1000000,     # Milhões
        'K': 1000         # Milhares
    }
    
    for suffix, multiplier in multipliers.items():
        if streams_text.endswith(suffix):
            number = streams_text[:-1]
            try:
                # Lidar com decimais como "1.43B"
                if '.' in number:
                    return int(float(number) * multiplier)
                else:
                    return int(float(number) * multiplier)
            except ValueError:
                return 0
    
    # Se não tem sufixo, tenta converter diretamente
    try:
        return int(float(streams_text))
    except ValueError:
        return 0

def scrape_selena_solo():
    """Faz scraping das músicas da Selena Gomez Solo"""
    url = "https://kworb.net/spotify/artist/0C8ZW7ezQVs4URX5aX7Kqx_songs.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"🔍 Conectando ao Kworb: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar a tabela principal
        table = soup.find('table', {'class': 'addpos'})
        
        if not table:
            print("❌ Tabela não encontrada!")
            return []
        
        songs = []
        position = 0
        
        # Percorrer linhas da tabela (pular cabeçalho)
        rows = table.find_all('tr')[1:]  # Pular primeira linha (cabeçalho)
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) >= 4:
                position += 1
                
                # Nome da música (segunda coluna)
                song_name = cells[1].text.strip()
                
                # Streams totais (terceira coluna)
                total_streams_text = cells[2].text.strip()
                total_streams = parse_streams(total_streams_text)
                
                # Streams diários (quarta coluna)
                daily_streams_text = cells[3].text.strip()
                daily_streams = parse_streams(daily_streams_text)
                
                # Remover ft. do nome para limpeza
                if 'ft.' in song_name.lower():
                    song_name = song_name.split('ft.')[0].strip()
                
                song_data = {
                    "name": song_name,
                    "artist": "Selena Gomez",
                    "total": total_streams,
                    "daily": daily_streams,
                    "goal": 0,  # Será calculado depois
                    "era": "solo",
                    "position": position
                }
                
                songs.append(song_data)
                print(f"  ✅ {position}. {song_name} - {total_streams:,} (diário: {daily_streams:,})")
        
        print(f"📊 Total de músicas coletadas (solo): {len(songs)}")
        return songs
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return []

def calculate_goals(songs):
    """Calcula metas automáticas baseadas nos streams atuais"""
    for song in songs:
        total = song["total"]
        
        # Definir meta como próximo marco (1M, 10M, 100M, 1B)
        if total < 1000000:  # Menos de 1M
            goal = 1000000
        elif total < 10000000:  # Menos de 10M
            goal = 10000000
        elif total < 100000000:  # Menos de 100M
            goal = 100000000
        elif total < 1000000000:  # Menos de 1B
            goal = 1000000000
        else:  # Mais de 1B
            goal = int(total * 1.1)  # 10% a mais
        
        song["goal"] = goal
    
    return songs

def save_to_json(songs, filename="data_solo.json"):
    """Salva os dados em arquivo JSON"""
    if not songs:
        print("⚠️ Nenhum dado para salvar!")
        return
    
    total_streams = sum(song["total"] for song in songs)
    
    data = {
        "last_update": get_brazil_time(),
        "total_streams": total_streams,
        "total_songs": len(songs),
        "songs": calculate_goals(songs)
    }
    
    # Garantir que a pasta existe
    os.makedirs('data', exist_ok=True)
    
    with open(f'data/{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Dados salvos em: data/{filename}")
    print(f"📈 Streams totais: {total_streams:,}")
    print(f"🕒 Atualizado em: {data['last_update']}")

def main():
    print("=" * 50)
    print("SCRAPER SELENA GOMEZ SOLO")
    print("=" * 50)
    
    songs = scrape_selena_solo()
    
    if songs:
        save_to_json(songs, "data_solo.json")
        print("✅ Scraping concluído com sucesso!")
    else:
        print("❌ Falha no scraping. Verifique a conexão.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
