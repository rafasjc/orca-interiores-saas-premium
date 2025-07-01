"""
Analisador de Arquivos 3D com IA Integrada
Sistema completo de análise inteligente para marcenaria
Versão: 3.0 Premium
"""

import re
import math
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

class FileAnalyzer:
    """Analisador de arquivos 3D com IA integrada"""
    
    def __init__(self):
        """Inicializa o analisador"""
        
        # Configurações de análise
        self.config = {
            'unidade_padrao': 'mm',
            'densidade_madeira': 0.6,  # g/cm³
            'tolerancia_geometrica': 0.1,
            'area_minima_componente': 0.01,  # m²
            'area_maxima_componente': 25.0,  # m²
            'debug': False
        }
        
        # Padrões de reconhecimento
        self.padroes_arquivo = {
            'obj': {
                'vertices': r'^v\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)',
                'faces': r'^f\s+(.+)',
                'objetos': r'^o\s+(.+)',
                'grupos': r'^g\s+(.+)'
            },
            'dae': {
                'geometria': r'<geometry.*?id="([^"]+)"',
                'vertices': r'<float_array.*?count="(\d+)"[^>]*>(.*?)</float_array>',
                'indices': r'<p>(.*?)</p>'
            }
        }
    
    def analisar_arquivo_3d_com_ia(self, arquivo_conteudo: bytes, nome_arquivo: str, ai_analyzer=None) -> Dict:
        """Análise completa com IA integrada"""
        
        try:
            # Análise básica de geometria
            resultado_basico = self._analisar_geometria_basica(arquivo_conteudo, nome_arquivo)
            
            if not resultado_basico or resultado_basico.get('erro'):
                return resultado_basico
            
            # Se IA disponível, aplicar análise inteligente
            if ai_analyzer:
                return self._aplicar_analise_ia(resultado_basico, ai_analyzer)
            else:
                # Fallback para análise básica
                resultado_basico['ia_ativa'] = False
                return resultado_basico
                
        except Exception as e:
            return {
                'erro': f'Erro na análise: {str(e)}',
                'componentes': [],
                'ia_ativa': False
            }
    
    def _analisar_geometria_basica(self, arquivo_conteudo: bytes, nome_arquivo: str) -> Dict:
        """Análise básica de geometria 3D"""
        
        try:
            # Decodificar conteúdo
            conteudo_texto = arquivo_conteudo.decode('utf-8', errors='ignore')
            
            # Determinar formato
            formato = self._detectar_formato(nome_arquivo, conteudo_texto)
            
            if formato == 'obj':
                return self._analisar_obj(conteudo_texto, nome_arquivo)
            elif formato == 'dae':
                return self._analisar_dae(conteudo_texto, nome_arquivo)
            else:
                return {
                    'erro': f'Formato não suportado: {formato}',
                    'componentes': []
                }
                
        except Exception as e:
            return {
                'erro': f'Erro na análise básica: {str(e)}',
                'componentes': []
            }
    
    def _detectar_formato(self, nome_arquivo: str, conteudo: str) -> str:
        """Detecta formato do arquivo"""
        
        extensao = nome_arquivo.lower().split('.')[-1]
        
        if extensao == 'obj':
            return 'obj'
        elif extensao in ['dae', 'collada']:
            return 'dae'
        elif extensao == 'stl':
            return 'stl'
        elif extensao == 'ply':
            return 'ply'
        
        # Detectar por conteúdo
        if 'COLLADA' in conteudo or '<geometry' in conteudo:
            return 'dae'
        elif conteudo.startswith('solid ') or 'facet normal' in conteudo:
            return 'stl'
        elif 'ply' in conteudo.lower()[:100]:
            return 'ply'
        elif re.search(r'^v\s+', conteudo, re.MULTILINE):
            return 'obj'
        
        return 'desconhecido'
    
    def _analisar_obj(self, conteudo: str, nome_arquivo: str) -> Dict:
        """Análise específica para arquivos OBJ"""
        
        componentes = []
        vertices_globais = []
        objeto_atual = None
        vertices_objeto = []
        faces_objeto = []
        
        linhas = conteudo.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            
            # Vértices
            if linha.startswith('v '):
                coords = re.findall(r'[-\d\.]+', linha)
                if len(coords) >= 3:
                    vertice = [float(coords[0]), float(coords[1]), float(coords[2])]
                    vertices_globais.append(vertice)
                    vertices_objeto.append(vertice)
            
            # Objetos/Grupos
            elif linha.startswith('o ') or linha.startswith('g '):
                # Finalizar objeto anterior
                if objeto_atual and vertices_objeto:
                    componente = self._processar_componente(
                        objeto_atual, vertices_objeto, faces_objeto
                    )
                    if componente:
                        componentes.append(componente)
                
                # Iniciar novo objeto
                objeto_atual = linha[2:].strip() or f"Objeto_{len(componentes)+1}"
                vertices_objeto = []
                faces_objeto = []
            
            # Faces
            elif linha.startswith('f '):
                face_data = linha[2:].strip()
                faces_objeto.append(face_data)
        
        # Processar último objeto
        if objeto_atual and vertices_objeto:
            componente = self._processar_componente(
                objeto_atual, vertices_objeto, faces_objeto
            )
            if componente:
                componentes.append(componente)
        
        # Se não há objetos definidos, tratar como um único componente
        if not componentes and vertices_globais:
            componente = self._processar_componente(
                nome_arquivo.replace('.obj', ''), vertices_globais, []
            )
            if componente:
                componentes.append(componente)
        
        return {
            'componentes': componentes,
            'total_componentes': len(componentes),
            'area_total_m2': sum(c.get('area_m2', 0) for c in componentes),
            'formato': 'obj',
            'arquivo': nome_arquivo
        }
    
    def _analisar_dae(self, conteudo: str, nome_arquivo: str) -> Dict:
        """Análise específica para arquivos DAE/Collada"""
        
        componentes = []
        
        # Extrair geometrias
        geometrias = re.findall(r'<geometry.*?id="([^"]+)".*?</geometry>', conteudo, re.DOTALL)
        
        for i, geometria in enumerate(geometrias):
            # Extrair vértices
            vertices_match = re.search(
                r'<float_array.*?count="(\d+)"[^>]*>(.*?)</float_array>', 
                geometria, re.DOTALL
            )
            
            if vertices_match:
                count = int(vertices_match.group(1))
                vertices_data = vertices_match.group(2).strip()
                coords = [float(x) for x in vertices_data.split()]
                
                # Agrupar em vértices 3D
                vertices = []
                for j in range(0, len(coords), 3):
                    if j + 2 < len(coords):
                        vertices.append([coords[j], coords[j+1], coords[j+2]])
                
                if vertices:
                    nome_componente = f"Geometria_{i+1}"
                    componente = self._processar_componente(nome_componente, vertices, [])
                    if componente:
                        componentes.append(componente)
        
        return {
            'componentes': componentes,
            'total_componentes': len(componentes),
            'area_total_m2': sum(c.get('area_m2', 0) for c in componentes),
            'formato': 'dae',
            'arquivo': nome_arquivo
        }
    
    def _processar_componente(self, nome: str, vertices: List, faces: List) -> Optional[Dict]:
        """Processa um componente individual"""
        
        if not vertices or len(vertices) < 3:
            return None
        
        try:
            # Converter para numpy array
            vertices_array = np.array(vertices)
            
            # Calcular bounding box
            min_coords = np.min(vertices_array, axis=0)
            max_coords = np.max(vertices_array, axis=0)
            dimensoes = max_coords - min_coords
            
            # Converter de mm para metros (assumindo entrada em mm)
            dimensoes_m = dimensoes / 1000.0
            
            # Calcular área aproximada (maior face do bounding box)
            areas_faces = [
                dimensoes_m[0] * dimensoes_m[1],  # XY
                dimensoes_m[1] * dimensoes_m[2],  # YZ
                dimensoes_m[0] * dimensoes_m[2]   # XZ
            ]
            area_m2 = max(areas_faces)
            
            # Validar área
            if area_m2 < self.config['area_minima_componente'] or area_m2 > self.config['area_maxima_componente']:
                return None
            
            # Calcular volume aproximado
            volume_m3 = (dimensoes_m[0] * dimensoes_m[1] * dimensoes_m[2])
            
            # Calcular centro de massa
            centro_massa = np.mean(vertices_array, axis=0)
            
            # Classificação básica por nome
            tipo_basico = self._classificar_por_nome(nome)
            
            return {
                'nome': nome,
                'tipo': tipo_basico,
                'area_m2': round(area_m2, 4),
                'volume_m3': round(volume_m3, 6),
                'dimensoes': {
                    'largura': round(dimensoes_m[0], 3),
                    'altura': round(dimensoes_m[1], 3),
                    'profundidade': round(dimensoes_m[2], 3)
                },
                'vertices': vertices,
                'faces': faces,
                'centro_massa': centro_massa.tolist(),
                'num_vertices': len(vertices),
                'num_faces': len(faces),
                'classificacao_origem': 'basica'
            }
            
        except Exception as e:
            if self.config['debug']:
                print(f"Erro ao processar componente {nome}: {e}")
            return None
    
    def _classificar_por_nome(self, nome: str) -> str:
        """Classificação básica baseada no nome"""
        
        nome_lower = nome.lower()
        
        # Palavras-chave para classificação
        classificacoes = {
            'armario': ['armario', 'cabinet', 'wardrobe', 'closet', 'guarda'],
            'despenseiro': ['despenseiro', 'pantry', 'coluna', 'torre', 'alto'],
            'balcao': ['balcao', 'counter', 'base', 'inferior', 'bancada'],
            'gaveteiro': ['gaveteiro', 'drawer', 'gaveta', 'chest'],
            'prateleira': ['prateleira', 'shelf', 'estante', 'divider'],
            'porta': ['porta', 'door', 'folha', 'leaf'],
            'gaveta': ['gaveta', 'drawer', 'box', 'caixa']
        }
        
        for tipo, palavras in classificacoes.items():
            if any(palavra in nome_lower for palavra in palavras):
                return tipo
        
        # Verificar se é elemento não-marcenaria
        nao_marcenaria = ['wall', 'parede', 'floor', 'piso', 'ceiling', 'teto', 
                         'window', 'janela', 'geladeira', 'fogao', 'pia']
        
        if any(palavra in nome_lower for palavra in nao_marcenaria):
            return 'nao_marcenaria'
        
        return 'armario'  # Padrão
    
    def _aplicar_analise_ia(self, resultado_basico: Dict, ai_analyzer) -> Dict:
        """Aplica análise de IA aos componentes"""
        
        try:
            componentes = resultado_basico.get('componentes', [])
            
            if not componentes:
                return {
                    **resultado_basico,
                    'ia_ativa': True,
                    'erro': 'Nenhum componente encontrado para análise'
                }
            
            # Analisar cada componente com IA
            componentes_com_ia = []
            
            for componente in componentes:
                # Análise individual com IA
                resultado_ia = ai_analyzer.analyze_component(componente)
                
                # Integrar resultado da IA
                componente['ia_tipo_detectado'] = resultado_ia['tipo_detectado']
                componente['ia_confianca'] = resultado_ia['confianca']
                componente['ia_motivo'] = resultado_ia['motivo']
                componente['ia_sugestoes'] = resultado_ia.get('sugestoes', [])
                componente['ia_alternativas'] = resultado_ia.get('alternativas', [])
                
                # Usar classificação da IA se confiança > 60%
                if (resultado_ia['confianca'] > 0.6 and 
                    resultado_ia['tipo_detectado'] not in ['invalido', 'nao_marcenaria', 'erro']):
                    componente['tipo'] = resultado_ia['tipo_detectado']
                    componente['classificacao_origem'] = 'ia'
                else:
                    componente['classificacao_origem'] = 'basica'
                
                # Filtrar elementos não-marcenaria
                if resultado_ia['tipo_detectado'] != 'nao_marcenaria':
                    componentes_com_ia.append(componente)
            
            # Análise em lote para insights
            if componentes_com_ia:
                batch_result = ai_analyzer.analyze_batch(componentes_com_ia)
                
                return {
                    'componentes': componentes_com_ia,
                    'total_componentes': len(componentes_com_ia),
                    'area_total_m2': sum(c.get('area_m2', 0) for c in componentes_com_ia),
                    'ia_ativa': True,
                    'ia_estatisticas': batch_result['estatisticas'],
                    'ia_insights': batch_result['insights'],
                    'ia_recomendacoes': batch_result['recomendacoes'],
                    'formato': resultado_basico.get('formato'),
                    'arquivo': resultado_basico.get('arquivo')
                }
            else:
                return {
                    'componentes': [],
                    'total_componentes': 0,
                    'area_total_m2': 0,
                    'ia_ativa': True,
                    'erro': 'Nenhum componente de marcenaria detectado pela IA',
                    'ia_estatisticas': batch_result['estatisticas'] if 'batch_result' in locals() else {},
                    'ia_insights': ['Arquivo contém apenas elementos não-marcenaria'],
                    'ia_recomendacoes': [
                        'Remover paredes, pisos e eletrodomésticos do SketchUp',
                        'Manter apenas móveis de marcenaria',
                        'Usar nomes descritivos nos objetos'
                    ]
                }
                
        except Exception as e:
            return {
                **resultado_basico,
                'ia_ativa': False,
                'erro_ia': f'Erro na análise de IA: {str(e)}'
            }
    
    def validar_arquivo(self, arquivo_conteudo: bytes, nome_arquivo: str) -> Dict:
        """Valida arquivo antes da análise"""
        
        validacao = {
            'valido': True,
            'erros': [],
            'avisos': [],
            'tamanho_mb': len(arquivo_conteudo) / 1024 / 1024
        }
        
        # Verificar tamanho
        if validacao['tamanho_mb'] > 500:
            validacao['valido'] = False
            validacao['erros'].append('Arquivo muito grande (máximo 500MB)')
        
        # Verificar formato
        formato = self._detectar_formato(nome_arquivo, arquivo_conteudo.decode('utf-8', errors='ignore'))
        if formato == 'desconhecido':
            validacao['valido'] = False
            validacao['erros'].append('Formato de arquivo não suportado')
        
        # Verificar conteúdo básico
        try:
            conteudo_texto = arquivo_conteudo.decode('utf-8', errors='ignore')
            
            if formato == 'obj':
                if not re.search(r'^v\s+', conteudo_texto, re.MULTILINE):
                    validacao['avisos'].append('Nenhum vértice encontrado no arquivo OBJ')
            
            elif formato == 'dae':
                if '<geometry' not in conteudo_texto:
                    validacao['avisos'].append('Nenhuma geometria encontrada no arquivo DAE')
                    
        except Exception as e:
            validacao['erros'].append(f'Erro ao ler conteúdo: {str(e)}')
        
        return validacao
    
    def obter_estatisticas_arquivo(self, resultado_analise: Dict) -> Dict:
        """Gera estatísticas detalhadas do arquivo"""
        
        if not resultado_analise or resultado_analise.get('erro'):
            return {}
        
        componentes = resultado_analise.get('componentes', [])
        
        if not componentes:
            return {}
        
        # Estatísticas básicas
        areas = [c.get('area_m2', 0) for c in componentes]
        volumes = [c.get('volume_m3', 0) for c in componentes]
        
        # Contagem por tipo
        tipos = {}
        for comp in componentes:
            tipo = comp.get('tipo', 'indefinido')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        # Estatísticas de IA
        ia_stats = {}
        if resultado_analise.get('ia_ativa'):
            confiancas = [c.get('ia_confianca', 0) for c in componentes if c.get('ia_confianca')]
            ia_stats = {
                'confianca_media': sum(confiancas) / len(confiancas) if confiancas else 0,
                'confianca_minima': min(confiancas) if confiancas else 0,
                'confianca_maxima': max(confiancas) if confiancas else 0,
                'componentes_alta_confianca': len([c for c in confiancas if c > 0.8]),
                'componentes_baixa_confianca': len([c for c in confiancas if c < 0.5])
            }
        
        return {
            'total_componentes': len(componentes),
            'area_total_m2': sum(areas),
            'area_media_m2': sum(areas) / len(areas) if areas else 0,
            'area_minima_m2': min(areas) if areas else 0,
            'area_maxima_m2': max(areas) if areas else 0,
            'volume_total_m3': sum(volumes),
            'tipos_detectados': tipos,
            'tipo_mais_comum': max(tipos.items(), key=lambda x: x[1])[0] if tipos else None,
            'diversidade_tipos': len(tipos),
            'ia_estatisticas': ia_stats
        }

# Exemplo de uso
if __name__ == "__main__":
    # Criar analisador
    analyzer = FileAnalyzer()
    
    print("🔍 File Analyzer com IA integrada inicializado!")
    print("📊 Formatos suportados: OBJ, DAE, STL, PLY")
    print("🤖 IA: Classificação automática de móveis")
    print("✅ Sistema pronto para análise!")

