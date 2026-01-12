#!/usr/bin/env python3
"""
Mescla dados da Selena Solo e Selena & The Scene em um único data.json
"""

import json
import os
from datetime import datetime
import pytz

def get_brazil_time():
    """Retorna data/hora atual no horário de Brasília"""
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %z')

def load_json(filename):
    """Carrega arquivo JSON com tratamento de erro"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Arquivo não encontrado: {filename}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Erro ao ler JSON: {filename}")
        return None

def merge_data():
    """Mescla dados de solo e banda em um único arquivo"""
    print("🔄 Mesclando dados da Selena Gomez...")
    
    # Carregar dados individuais
    data_solo = load_json('data/data_solo.json')
    data_band = load_json('data/data_band.json')
    
    all_songs = []
    total_streams = 0
    
    # Processar músicas solo
    if data_solo and 'songs' in data_solo:
        all_songs.extend(data_solo['songs'])
        total_streams += data_solo.get('total_streams', 0)
        print(f"📥 {len(data_solo['songs'])} músicas solo carregadas")
    
    # Processar músicas da banda
    if data_band and 'songs' in data_band:
        all_songs.extend(data_band['songs'])
        total_streams += data_band.get('total_streams', 0)
        print(f"📥 {len(data_band['songs'])} músicas da banda carregadas")
    
    if not all_songs:
        print("❌ Nenhum dado para mesclar!")
        return False
    
    # Reordenar por streams totais (da maior para menor)
    all_songs.sort(key=lambda x: x['total'], reverse=True)
    
    # Atualizar posições
    for i, song in enumerate(all_songs, 1):
        song['position'] = i
    
    # Criar estrutura final
    merged_data = {
        "last_update": get_brazil_time(),
        "total_streams": total_streams,
        "total_songs": len(all_songs),
        "songs": all_songs
    }
    
    # Salvar arquivo principal
    with open('data/data.json', 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Arquivo mesclado salvo: data/data.json")
    print(f"📊 Total de músicas: {len(all_songs)}")
    print(f"📈 Streams totais: {total_streams:,}")
    print(f"🏆 Top 5 músicas:")
    
    for i, song in enumerate(all_songs[:5], 1):
        print(f"   {i}. {song['name']} - {song['total']:,} ({song['era']})")
    
    return True

def main():
    print("=" * 50)
    print("MESCLADOR DE DADOS - SELENA GOMEZ")
    print("=" * 50)
    
    # Garantir que a pasta data existe
    os.makedirs('data', exist_ok=True)
    
    if merge_data():
        print("✅ Mesclagem concluída com sucesso!")
    else:
        print("❌ Falha na mesclagem.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
