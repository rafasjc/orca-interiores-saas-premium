"""
IA Analyzer - Protótipo de Análise Inteligente de Móveis 3D
Sistema de classificação automática baseado em geometria e padrões
Versão: 1.0 - Implementação Básica
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
import math

@dataclass
class ComponenteAnalise:
    """Estrutura para análise de componente 3D"""
    nome: str
    area_m2: float
    volume_m3: float
    dimensoes: Tuple[float, float, float]  # largura, altura, profundidade
    vertices: List
    faces: List
    centro_massa: Tuple[float, float, float]
    
class AIAnalyzer:
    """Sistema de IA para análise inteligente de móveis 3D"""
    
    def __init__(self):
        """Inicializa o analisador de IA"""
        
        # Base de conhecimento de móveis
        self.knowledge_base = self._build_knowledge_base()
        
        # Palavras-chave para classificação
        self.keywords = self._build_keywords()
        
        # Padrões geométricos
        self.geometric_patterns = self._build_geometric_patterns()
        
        # Configurações de validação
        self.validation_rules = self._build_validation_rules()
        
        # Métricas de confiança
        self.confidence_weights = {
            'geometric': 0.4,    # 40% baseado em geometria
            'dimensional': 0.3,  # 30% baseado em dimensões
            'semantic': 0.2,     # 20% baseado em nome/contexto
            'structural': 0.1    # 10% baseado em estrutura
        }
    
    def _build_knowledge_base(self) -> Dict:
        """Constrói base de conhecimento de móveis"""
        
        return {
            'armario': {
                'dimensoes_tipicas': {
                    'largura': (400, 1200),    # 40cm a 120cm
                    'altura': (600, 2400),     # 60cm a 240cm
                    'profundidade': (300, 600) # 30cm a 60cm
                },
                'proporcoes': {
                    'altura_largura': (0.5, 4.0),    # Altura/Largura
                    'profundidade_largura': (0.25, 1.5) # Prof/Largura
                },
                'area_tipica': (0.5, 8.0),  # 0.5m² a 8m²
                'volume_tipico': (0.1, 3.0), # 0.1m³ a 3m³
                'keywords': ['armario', 'cabinet', 'wardrobe', 'closet', 'guarda']
            },
            
            'despenseiro': {
                'dimensoes_tipicas': {
                    'largura': (300, 1000),
                    'altura': (1800, 2600),    # Móveis altos
                    'profundidade': (300, 600)
                },
                'proporcoes': {
                    'altura_largura': (1.8, 8.0),    # Muito alto
                    'profundidade_largura': (0.3, 2.0)
                },
                'area_tipica': (1.0, 6.0),
                'volume_tipico': (0.5, 4.0),
                'keywords': ['despenseiro', 'pantry', 'tall', 'alto', 'coluna']
            },
            
            'balcao': {
                'dimensoes_tipicas': {
                    'largura': (300, 1200),
                    'altura': (700, 900),      # Altura de bancada
                    'profundidade': (400, 700)
                },
                'proporcoes': {
                    'altura_largura': (0.3, 2.0),    # Mais largo que alto
                    'profundidade_largura': (0.5, 2.0)
                },
                'area_tipica': (0.3, 3.0),
                'volume_tipico': (0.2, 2.0),
                'keywords': ['balcao', 'counter', 'base', 'inferior', 'bancada']
            },
            
            'gaveteiro': {
                'dimensoes_tipicas': {
                    'largura': (300, 800),
                    'altura': (200, 800),      # Relativamente baixo
                    'profundidade': (300, 600)
                },
                'proporcoes': {
                    'altura_largura': (0.25, 2.0),   # Mais largo que alto
                    'profundidade_largura': (0.5, 2.0)
                },
                'area_tipica': (0.2, 2.0),
                'volume_tipico': (0.1, 1.0),
                'keywords': ['gaveteiro', 'drawer', 'gaveta', 'chest']
            },
            
            'prateleira': {
                'dimensoes_tipicas': {
                    'largura': (200, 1200),
                    'altura': (15, 50),        # Muito fina
                    'profundidade': (200, 600)
                },
                'proporcoes': {
                    'altura_largura': (0.01, 0.25),  # Muito plana
                    'profundidade_largura': (0.2, 3.0)
                },
                'area_tipica': (0.1, 2.0),
                'volume_tipica': (0.01, 0.1),
                'keywords': ['prateleira', 'shelf', 'estante', 'divider']
            },
            
            'porta': {
                'dimensoes_tipicas': {
                    'largura': (300, 800),
                    'altura': (400, 2000),
                    'profundidade': (15, 25)   # Muito fina
                },
                'proporcoes': {
                    'altura_largura': (1.0, 6.0),    # Mais alta que larga
                    'profundidade_largura': (0.02, 0.1) # Muito fina
                },
                'area_tipica': (0.2, 1.5),
                'volume_tipico': (0.005, 0.05),
                'keywords': ['porta', 'door', 'folha', 'leaf']
            },
            
            'gaveta': {
                'dimensoes_tipicas': {
                    'largura': (200, 800),
                    'altura': (80, 300),       # Baixa
                    'profundidade': (300, 600)
                },
                'proporcoes': {
                    'altura_largura': (0.1, 1.5),    # Mais larga que alta
                    'profundidade_largura': (0.5, 3.0)
                },
                'area_tipica': (0.1, 1.5),
                'volume_tipico': (0.05, 0.5),
                'keywords': ['gaveta', 'drawer', 'box', 'caixa']
            }
        }
    
    def _build_keywords(self) -> Dict:
        """Constrói dicionário de palavras-chave"""
        
        keywords = {
            'marcenaria': [
                'armario', 'cabinet', 'wardrobe', 'closet', 'guarda',
                'despenseiro', 'pantry', 'coluna', 'torre',
                'balcao', 'counter', 'base', 'inferior',
                'gaveteiro', 'drawer', 'gaveta', 'chest',
                'prateleira', 'shelf', 'estante',
                'porta', 'door', 'folha',
                'movel', 'furniture', 'mobile'
            ],
            
            'nao_marcenaria': [
                'wall', 'parede', 'muro',
                'floor', 'piso', 'chao',
                'ceiling', 'teto', 'laje',
                'window', 'janela', 'vidro',
                'door_frame', 'batente', 'marco',
                'pipe', 'tubo', 'cano',
                'wire', 'fio', 'cabo',
                'light', 'luz', 'lampada',
                'outlet', 'tomada', 'interruptor'
            ],
            
            'eletrodomesticos': [
                'geladeira', 'refrigerator', 'fridge',
                'fogao', 'stove', 'cooktop',
                'microondas', 'microwave',
                'lava', 'dishwasher', 'washing',
                'forno', 'oven'
            ]
        }
        
        return keywords
    
    def _build_geometric_patterns(self) -> Dict:
        """Constrói padrões geométricos para classificação"""
        
        return {
            'muito_plano': {
                'condicao': lambda dims: min(dims) / max(dims) < 0.05,
                'tipos_possiveis': ['prateleira', 'porta', 'tampo']
            },
            
            'muito_alto': {
                'condicao': lambda dims: dims[1] > 1800,  # Altura > 180cm
                'tipos_possiveis': ['despenseiro', 'armario']
            },
            
            'altura_bancada': {
                'condicao': lambda dims: 700 <= dims[1] <= 900,  # 70-90cm
                'tipos_possiveis': ['balcao', 'gaveteiro']
            },
            
            'muito_baixo': {
                'condicao': lambda dims: dims[1] < 400,  # Altura < 40cm
                'tipos_possiveis': ['gaveta', 'prateleira', 'rodape']
            },
            
            'proporcao_gaveta': {
                'condicao': lambda dims: dims[2] > dims[1] and dims[0] > dims[1],
                'tipos_possiveis': ['gaveta', 'gaveteiro']
            }
        }
    
    def _build_validation_rules(self) -> Dict:
        """Constrói regras de validação"""
        
        return {
            'dimensao_maxima': 5000,      # 5 metros máximo
            'dimensao_minima': 10,        # 1cm mínimo
            'area_maxima': 25.0,          # 25m² máximo
            'area_minima': 0.01,          # 100cm² mínimo
            'volume_maximo': 10.0,        # 10m³ máximo
            'volume_minimo': 0.001,       # 1 litro mínimo
            'proporcao_maxima': 100.0,    # Proporção máxima 100:1
            'densidade_minima': 0.1,      # Densidade mínima (volume/área)
            'densidade_maxima': 2.0       # Densidade máxima
        }
    
    def analyze_component(self, componente: Dict) -> Dict:
        """Analisa um componente 3D e retorna classificação inteligente"""
        
        try:
            # Converter para estrutura de análise
            comp_analise = self._convert_to_analysis_structure(componente)
            
            # Validar componente
            validation_result = self._validate_component(comp_analise)
            
            if not validation_result['is_valid']:
                return {
                    'tipo_detectado': 'invalido',
                    'confianca': 0.0,
                    'motivo': validation_result['reason'],
                    'sugestoes': validation_result['suggestions']
                }
            
            # Análise semântica (nome)
            semantic_analysis = self._analyze_semantic(comp_analise)
            
            # Análise geométrica
            geometric_analysis = self._analyze_geometry(comp_analise)
            
            # Análise dimensional
            dimensional_analysis = self._analyze_dimensions(comp_analise)
            
            # Análise estrutural
            structural_analysis = self._analyze_structure(comp_analise)
            
            # Combinar análises
            final_classification = self._combine_analyses(
                semantic_analysis,
                geometric_analysis,
                dimensional_analysis,
                structural_analysis
            )
            
            return final_classification
            
        except Exception as e:
            return {
                'tipo_detectado': 'erro',
                'confianca': 0.0,
                'motivo': f'Erro na análise: {str(e)}',
                'sugestoes': ['Verificar formato do arquivo', 'Tentar novamente']
            }
    
    def _convert_to_analysis_structure(self, componente: Dict) -> ComponenteAnalise:
        """Converte componente para estrutura de análise"""
        
        # Extrair dimensões
        vertices = componente.get('vertices', [])
        if vertices:
            # Calcular bounding box
            vertices_array = np.array(vertices)
            min_coords = np.min(vertices_array, axis=0)
            max_coords = np.max(vertices_array, axis=0)
            dimensoes = tuple(max_coords - min_coords)
            centro_massa = tuple(np.mean(vertices_array, axis=0))
        else:
            # Usar dimensões fornecidas ou padrão
            dimensoes = componente.get('dimensoes', (100, 100, 100))
            centro_massa = (0, 0, 0)
        
        # Calcular volume aproximado
        volume_m3 = (dimensoes[0] * dimensoes[1] * dimensoes[2]) / 1000000000  # mm³ para m³
        
        return ComponenteAnalise(
            nome=componente.get('nome', 'Componente'),
            area_m2=componente.get('area_m2', 0.0),
            volume_m3=volume_m3,
            dimensoes=dimensoes,
            vertices=vertices,
            faces=componente.get('faces', []),
            centro_massa=centro_massa
        )
    
    def _validate_component(self, comp: ComponenteAnalise) -> Dict:
        """Valida se componente é válido para análise"""
        
        rules = self.validation_rules
        
        # Verificar dimensões
        max_dim = max(comp.dimensoes)
        min_dim = min(comp.dimensoes)
        
        if max_dim > rules['dimensao_maxima']:
            return {
                'is_valid': False,
                'reason': f'Dimensão muito grande: {max_dim:.1f}mm',
                'suggestions': ['Verificar escala do arquivo', 'Pode ser elemento estrutural']
            }
        
        if min_dim < rules['dimensao_minima']:
            return {
                'is_valid': False,
                'reason': f'Dimensão muito pequena: {min_dim:.1f}mm',
                'suggestions': ['Verificar se não é detalhe', 'Pode ser ruído na geometria']
            }
        
        # Verificar área
        if comp.area_m2 > rules['area_maxima']:
            return {
                'is_valid': False,
                'reason': f'Área muito grande: {comp.area_m2:.2f}m²',
                'suggestions': ['Provavelmente parede ou piso', 'Filtrar elementos estruturais']
            }
        
        if comp.area_m2 < rules['area_minima']:
            return {
                'is_valid': False,
                'reason': f'Área muito pequena: {comp.area_m2:.4f}m²',
                'suggestions': ['Pode ser acessório', 'Verificar relevância']
            }
        
        # Verificar proporções
        proporcao = max_dim / min_dim
        if proporcao > rules['proporcao_maxima']:
            return {
                'is_valid': False,
                'reason': f'Proporção muito extrema: {proporcao:.1f}:1',
                'suggestions': ['Pode ser elemento linear', 'Verificar geometria']
            }
        
        # Verificar densidade (volume/área)
        if comp.area_m2 > 0:
            densidade = comp.volume_m3 / comp.area_m2
            
            if densidade < rules['densidade_minima']:
                return {
                    'is_valid': False,
                    'reason': f'Densidade muito baixa: {densidade:.3f}',
                    'suggestions': ['Pode ser elemento muito fino', 'Verificar cálculo de volume']
                }
            
            if densidade > rules['densidade_maxima']:
                return {
                    'is_valid': False,
                    'reason': f'Densidade muito alta: {densidade:.3f}',
                    'suggestions': ['Pode ser elemento muito espesso', 'Verificar geometria']
                }
        
        return {
            'is_valid': True,
            'reason': 'Componente válido',
            'suggestions': []
        }
    
    def _analyze_semantic(self, comp: ComponenteAnalise) -> Dict:
        """Análise semântica baseada no nome"""
        
        nome_lower = comp.nome.lower()
        
        # Verificar se é marcenaria
        is_marcenaria = any(keyword in nome_lower for keyword in self.keywords['marcenaria'])
        is_nao_marcenaria = any(keyword in nome_lower for keyword in self.keywords['nao_marcenaria'])
        is_eletrodomestico = any(keyword in nome_lower for keyword in self.keywords['eletrodomesticos'])
        
        if is_nao_marcenaria or is_eletrodomestico:
            return {
                'tipo': 'nao_marcenaria',
                'confianca': 0.9,
                'motivo': 'Nome indica elemento não-marcenaria'
            }
        
        # Tentar classificar tipo específico
        for tipo, info in self.knowledge_base.items():
            if any(keyword in nome_lower for keyword in info['keywords']):
                return {
                    'tipo': tipo,
                    'confianca': 0.8,
                    'motivo': f'Nome indica {tipo}'
                }
        
        # Se contém palavra de marcenaria mas não específica
        if is_marcenaria:
            return {
                'tipo': 'armario',  # Padrão
                'confianca': 0.5,
                'motivo': 'Nome indica marcenaria genérica'
            }
        
        # Nome não conclusivo
        return {
            'tipo': 'indefinido',
            'confianca': 0.1,
            'motivo': 'Nome não conclusivo'
        }
    
    def _analyze_geometry(self, comp: ComponenteAnalise) -> Dict:
        """Análise geométrica baseada em padrões"""
        
        matches = []
        
        for pattern_name, pattern_info in self.geometric_patterns.items():
            if pattern_info['condicao'](comp.dimensoes):
                matches.append({
                    'pattern': pattern_name,
                    'tipos_possiveis': pattern_info['tipos_possiveis'],
                    'confianca': 0.7
                })
        
        if matches:
            # Pegar o padrão mais específico
            best_match = matches[0]
            return {
                'tipo': best_match['tipos_possiveis'][0],
                'confianca': best_match['confianca'],
                'motivo': f'Padrão geométrico: {best_match["pattern"]}',
                'alternativas': best_match['tipos_possiveis'][1:] if len(best_match['tipos_possiveis']) > 1 else []
            }
        
        return {
            'tipo': 'indefinido',
            'confianca': 0.2,
            'motivo': 'Nenhum padrão geométrico identificado'
        }
    
    def _analyze_dimensions(self, comp: ComponenteAnalise) -> Dict:
        """Análise dimensional baseada em conhecimento"""
        
        best_matches = []
        
        for tipo, info in self.knowledge_base.items():
            score = 0
            reasons = []
            
            # Verificar dimensões típicas
            dims_score = 0
            for i, dim_name in enumerate(['largura', 'altura', 'profundidade']):
                dim_range = info['dimensoes_tipicas'][dim_name]
                if dim_range[0] <= comp.dimensoes[i] <= dim_range[1]:
                    dims_score += 1
                    reasons.append(f'{dim_name} típica')
            
            score += (dims_score / 3) * 0.4  # 40% do score
            
            # Verificar proporções
            altura_largura = comp.dimensoes[1] / comp.dimensoes[0] if comp.dimensoes[0] > 0 else 0
            prof_largura = comp.dimensoes[2] / comp.dimensoes[0] if comp.dimensoes[0] > 0 else 0
            
            prop_ranges = info['proporcoes']
            prop_score = 0
            
            if prop_ranges['altura_largura'][0] <= altura_largura <= prop_ranges['altura_largura'][1]:
                prop_score += 1
                reasons.append('proporção altura/largura típica')
            
            if prop_ranges['profundidade_largura'][0] <= prof_largura <= prop_ranges['profundidade_largura'][1]:
                prop_score += 1
                reasons.append('proporção profundidade/largura típica')
            
            score += (prop_score / 2) * 0.3  # 30% do score
            
            # Verificar área
            area_range = info['area_tipica']
            if area_range[0] <= comp.area_m2 <= area_range[1]:
                score += 0.2  # 20% do score
                reasons.append('área típica')
            
            # Verificar volume
            if 'volume_tipico' in info:
                vol_range = info['volume_tipico']
                if vol_range[0] <= comp.volume_m3 <= vol_range[1]:
                    score += 0.1  # 10% do score
                    reasons.append('volume típico')
            
            if score > 0.3:  # Threshold mínimo
                best_matches.append({
                    'tipo': tipo,
                    'score': score,
                    'reasons': reasons
                })
        
        if best_matches:
            # Ordenar por score
            best_matches.sort(key=lambda x: x['score'], reverse=True)
            best = best_matches[0]
            
            return {
                'tipo': best['tipo'],
                'confianca': min(best['score'], 0.9),
                'motivo': f'Dimensões compatíveis: {", ".join(best["reasons"])}',
                'alternativas': [match['tipo'] for match in best_matches[1:3]]  # Top 3
            }
        
        return {
            'tipo': 'indefinido',
            'confianca': 0.1,
            'motivo': 'Dimensões não compatíveis com tipos conhecidos'
        }
    
    def _analyze_structure(self, comp: ComponenteAnalise) -> Dict:
        """Análise estrutural baseada em complexidade"""
        
        # Análise básica de complexidade
        num_vertices = len(comp.vertices)
        num_faces = len(comp.faces)
        
        # Calcular complexidade relativa
        if num_vertices > 0:
            complexidade = num_faces / num_vertices if num_vertices > 0 else 0
        else:
            complexidade = 0
        
        # Classificar baseado em complexidade
        if complexidade > 3.0:
            return {
                'tipo': 'complexo',
                'confianca': 0.6,
                'motivo': f'Geometria complexa ({num_faces} faces, {num_vertices} vértices)'
            }
        elif complexidade > 1.5:
            return {
                'tipo': 'medio',
                'confianca': 0.5,
                'motivo': f'Geometria média ({num_faces} faces, {num_vertices} vértices)'
            }
        else:
            return {
                'tipo': 'simples',
                'confianca': 0.4,
                'motivo': f'Geometria simples ({num_faces} faces, {num_vertices} vértices)'
            }
    
    def _combine_analyses(self, semantic: Dict, geometric: Dict, 
                         dimensional: Dict, structural: Dict) -> Dict:
        """Combina todas as análises para classificação final"""
        
        # Coletar candidatos
        candidates = {}
        
        # Adicionar candidatos de cada análise
        analyses = [
            ('semantic', semantic),
            ('geometric', geometric),
            ('dimensional', dimensional)
        ]
        
        for analysis_type, analysis in analyses:
            if analysis['tipo'] not in ['indefinido', 'nao_marcenaria', 'invalido', 'erro']:
                tipo = analysis['tipo']
                if tipo not in candidates:
                    candidates[tipo] = {
                        'scores': {},
                        'reasons': [],
                        'total_score': 0
                    }
                
                weight = self.confidence_weights.get(analysis_type, 0.1)
                score = analysis['confianca'] * weight
                
                candidates[tipo]['scores'][analysis_type] = score
                candidates[tipo]['reasons'].append(f"{analysis_type}: {analysis['motivo']}")
                candidates[tipo]['total_score'] += score
        
        # Verificar se é não-marcenaria
        if semantic['tipo'] == 'nao_marcenaria':
            return {
                'tipo_detectado': 'nao_marcenaria',
                'confianca': semantic['confianca'],
                'motivo': semantic['motivo'],
                'sugestoes': ['Filtrar este elemento', 'Não incluir no orçamento'],
                'detalhes': {
                    'semantic': semantic,
                    'geometric': geometric,
                    'dimensional': dimensional,
                    'structural': structural
                }
            }
        
        # Se não há candidatos válidos
        if not candidates:
            return {
                'tipo_detectado': 'indefinido',
                'confianca': 0.2,
                'motivo': 'Não foi possível classificar com confiança',
                'sugestoes': ['Verificar nome do objeto', 'Verificar dimensões', 'Classificar manualmente'],
                'detalhes': {
                    'semantic': semantic,
                    'geometric': geometric,
                    'dimensional': dimensional,
                    'structural': structural
                }
            }
        
        # Encontrar melhor candidato
        best_candidate = max(candidates.items(), key=lambda x: x[1]['total_score'])
        tipo_final = best_candidate[0]
        info_final = best_candidate[1]
        
        # Calcular confiança final
        confianca_final = min(info_final['total_score'], 0.95)
        
        # Gerar sugestões
        sugestoes = []
        if confianca_final < 0.5:
            sugestoes.append('Baixa confiança - verificar manualmente')
        if confianca_final < 0.7:
            sugestoes.append('Considerar classificação alternativa')
        
        # Alternativas
        alternativas = [tipo for tipo, info in sorted(candidates.items(), 
                       key=lambda x: x[1]['total_score'], reverse=True)[1:3]]
        
        return {
            'tipo_detectado': tipo_final,
            'confianca': round(confianca_final, 3),
            'motivo': '; '.join(info_final['reasons']),
            'sugestoes': sugestoes,
            'alternativas': alternativas,
            'detalhes': {
                'scores_por_analise': info_final['scores'],
                'semantic': semantic,
                'geometric': geometric,
                'dimensional': dimensional,
                'structural': structural
            }
        }
    
    def analyze_batch(self, componentes: List[Dict]) -> Dict:
        """Analisa múltiplos componentes e retorna análise do conjunto"""
        
        resultados = []
        estatisticas = {
            'total': len(componentes),
            'validos': 0,
            'marcenaria': 0,
            'nao_marcenaria': 0,
            'indefinidos': 0,
            'tipos_detectados': {},
            'confianca_media': 0.0
        }
        
        for componente in componentes:
            resultado = self.analyze_component(componente)
            resultados.append(resultado)
            
            # Atualizar estatísticas
            tipo = resultado['tipo_detectado']
            confianca = resultado['confianca']
            
            if tipo not in ['invalido', 'erro']:
                estatisticas['validos'] += 1
                
                if tipo == 'nao_marcenaria':
                    estatisticas['nao_marcenaria'] += 1
                elif tipo == 'indefinido':
                    estatisticas['indefinidos'] += 1
                else:
                    estatisticas['marcenaria'] += 1
                    
                    if tipo not in estatisticas['tipos_detectados']:
                        estatisticas['tipos_detectados'][tipo] = 0
                    estatisticas['tipos_detectados'][tipo] += 1
        
        # Calcular confiança média
        if estatisticas['validos'] > 0:
            confiancas = [r['confianca'] for r in resultados if r['tipo_detectado'] not in ['invalido', 'erro']]
            estatisticas['confianca_media'] = sum(confiancas) / len(confiancas)
        
        # Gerar insights
        insights = self._generate_insights(estatisticas)
        
        return {
            'resultados': resultados,
            'estatisticas': estatisticas,
            'insights': insights,
            'recomendacoes': self._generate_recommendations(estatisticas)
        }
    
    def _generate_insights(self, stats: Dict) -> List[str]:
        """Gera insights baseados nas estatísticas"""
        
        insights = []
        
        # Taxa de sucesso
        if stats['total'] > 0:
            taxa_validos = stats['validos'] / stats['total']
            if taxa_validos > 0.9:
                insights.append(f"✅ Excelente qualidade: {taxa_validos:.1%} dos componentes são válidos")
            elif taxa_validos > 0.7:
                insights.append(f"👍 Boa qualidade: {taxa_validos:.1%} dos componentes são válidos")
            else:
                insights.append(f"⚠️ Qualidade baixa: apenas {taxa_validos:.1%} dos componentes são válidos")
        
        # Proporção marcenaria vs não-marcenaria
        if stats['validos'] > 0:
            taxa_marcenaria = stats['marcenaria'] / stats['validos']
            if taxa_marcenaria > 0.8:
                insights.append(f"🎯 Arquivo bem preparado: {taxa_marcenaria:.1%} é marcenaria")
            elif taxa_marcenaria > 0.5:
                insights.append(f"📊 Arquivo misto: {taxa_marcenaria:.1%} é marcenaria")
            else:
                insights.append(f"⚠️ Muitos elementos não-marcenaria: apenas {taxa_marcenaria:.1%} é marcenaria")
        
        # Confiança média
        if stats['confianca_media'] > 0.8:
            insights.append(f"🎯 Alta confiança: {stats['confianca_media']:.1%} média")
        elif stats['confianca_media'] > 0.6:
            insights.append(f"👍 Confiança moderada: {stats['confianca_media']:.1%} média")
        else:
            insights.append(f"⚠️ Baixa confiança: {stats['confianca_media']:.1%} média")
        
        # Tipos mais comuns
        if stats['tipos_detectados']:
            tipo_mais_comum = max(stats['tipos_detectados'].items(), key=lambda x: x[1])
            insights.append(f"📈 Tipo mais comum: {tipo_mais_comum[0]} ({tipo_mais_comum[1]} ocorrências)")
        
        return insights
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """Gera recomendações baseadas nas estatísticas"""
        
        recomendacoes = []
        
        # Recomendações baseadas na qualidade
        if stats['total'] > 0:
            taxa_validos = stats['validos'] / stats['total']
            if taxa_validos < 0.7:
                recomendacoes.append("🔧 Melhorar preparação do arquivo 3D")
                recomendacoes.append("📏 Verificar escala e unidades")
        
        # Recomendações baseadas na proporção
        if stats['validos'] > 0:
            taxa_marcenaria = stats['marcenaria'] / stats['validos']
            if taxa_marcenaria < 0.5:
                recomendacoes.append("🎯 Remover elementos não-marcenaria do SketchUp")
                recomendacoes.append("🏠 Manter apenas móveis e componentes de madeira")
        
        # Recomendações baseadas na confiança
        if stats['confianca_media'] < 0.6:
            recomendacoes.append("📝 Usar nomes mais descritivos nos objetos")
            recomendacoes.append("📐 Verificar se dimensões estão realistas")
        
        # Recomendações baseadas nos indefinidos
        if stats['indefinidos'] > stats['marcenaria'] * 0.3:  # Mais de 30% indefinidos
            recomendacoes.append("🔍 Revisar objetos indefinidos manualmente")
            recomendacoes.append("🏷️ Adicionar tags ou grupos no SketchUp")
        
        return recomendacoes

# Exemplo de uso
if __name__ == "__main__":
    # Criar analisador
    analyzer = AIAnalyzer()
    
    # Exemplo de componente
    componente_exemplo = {
        'nome': 'Armario_Superior_Cozinha',
        'area_m2': 2.5,
        'vertices': [[0, 0, 0], [800, 0, 0], [800, 600, 0], [0, 600, 0],
                    [0, 0, 350], [800, 0, 350], [800, 600, 350], [0, 600, 350]],
        'faces': [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], 
                 [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    }
    
    # Analisar
    resultado = analyzer.analyze_component(componente_exemplo)
    
    print("🤖 Resultado da Análise de IA:")
    print(f"Tipo detectado: {resultado['tipo_detectado']}")
    print(f"Confiança: {resultado['confianca']:.1%}")
    print(f"Motivo: {resultado['motivo']}")
    
    if resultado.get('sugestoes'):
        print("Sugestões:")
        for sugestao in resultado['sugestoes']:
            print(f"  - {sugestao}")
    
    if resultado.get('alternativas'):
        print(f"Alternativas: {', '.join(resultado['alternativas'])}")

