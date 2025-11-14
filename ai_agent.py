#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent for generating personalized job application emails
Uses OpenAI GPT to create tailored cover letters based on user profile and job offers
"""

import openai
import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class AIJobApplicationAgent:
    """AI agent that generates personalized job application emails for multiple users"""
    
    def __init__(self):
        """Initialize the AI agent with user profiles and OpenAI configuration"""
        self.user_profiles = self._load_user_profiles()
        self.setup_openai()
    
    def setup_openai(self):
        """Setup OpenAI API configuration"""
        # Try to get API key from environment variables first
        api_key = os.getenv('OPENAI_API_KEY')
        
        # If not found, try to load from config.json
        if not api_key and os.path.exists('config.json'):
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'ai_settings' in config and 'openai_api_key' in config['ai_settings']:
                        api_key = config['ai_settings']['openai_api_key']
                        if api_key and 'sk-' in api_key:
                            os.environ['OPENAI_API_KEY'] = api_key
                            logger.info("OpenAI API key loaded from config.json")
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        if not api_key:
            logger.warning("OpenAI API key not found in environment variables or config file")
            return
        
        openai.api_key = api_key
        logger.info("OpenAI API configured successfully")
    
    def _load_user_profiles(self) -> Dict:
        """Load multiple user profiles data"""
        return {
            "damian": {
                "user_id": "damian",
                "email": "diazzdamian00@gmail.com",
                "nombre_completo": "Damián Gonzalo Díaz",
                "edad": 26,
                "ubicacion": "San Fernando, Buenos Aires",
                "telefono": "1132662924",
                "linkedin": "linkedin.com/in/damián-gonzalo-díaz",
            
            "educacion": {
                "carrera_principal": {
                    "titulo": "Abogacía",
                    "universidad": "Universidad de Buenos Aires - Facultad de Derecho",
                    "periodo": "2023 - En curso",
                    "estado": "Cursando actualmente"
                },
                "carrera_secundaria": {
                    "titulo": "Lic. Periodismo con Orientación en Deportes",
                    "institucion": "Instituto Sudamericano para la Enseñanza de la Comunicación",
                    "periodo": "2018 - 2020"
                },
                "idiomas": {
                    "ingles": {
                        "institucion": "C.A.B.S.I - Escuela de Inglés",
                        "nivel": "C1",
                        "periodo": "2015 - 2018"
                    }
                }
            },
            
            "experiencia_laboral": [
                {
                    "puesto": "Paralegal",
                    "empresa": "Estudio Arana",
                    "periodo": "2021 - 2025",
                    "estado": "Actual",
                    "responsabilidades": [
                        "Redacción de escritos, contratos y apelaciones",
                        "Procuración de expedientes en CABA y PBA",
                        "Trámites ante IGJ, Colescba"
                    ],
                    "habilidades_desarrolladas": [
                        "Redacción jurídica",
                        "Análisis de contratos",
                        "Seguimiento de expedientes",
                        "Trámites administrativos",
                        "Procuración judicial"
                    ]
                },
                {
                    "puesto": "Ayudante de Cátedra",
                    "empresa": "Facultad de Derecho - UBA",
                    "catedra": "Derechos Humanos y Garantías (Abramovich - Pulvirenti)",
                    "periodo": "2024 - En Curso",
                    "estado": "Actual",
                    "responsabilidades": [
                        "Dictado de clase sobre IA y Derechos Humanos"
                    ],
                    "habilidades_desarrolladas": [
                        "Docencia universitaria",
                        "Investigación en Derechos Humanos",
                        "Análisis de tecnología y derecho",
                        "Comunicación académica"
                    ]
                }
            ],
            
            "habilidades_tecnicas": [
                "Trabajo en equipo",
                "Análisis de contratos",
                "Seguimiento de expedientes",
                "Buenas relaciones laborales",
                "Redacción jurídica",
                "Boletín Oficial",
                "MEV",
                "SCBA",
                "PJN",
                "Lex Doctor",
                "IGJ",
                "Paquete Office"
            ],
            
            "habilidades_blandas": [
                "Comunicación oral y escrita",
                "Trabajo en equipo",
                "Adaptabilidad",
                "Responsabilidad",
                "Puntualidad",
                "Orientación al cliente",
                "Resolución de problemas",
                "Manejo de situaciones de presión"
            ],
            
            "idiomas": [
                {
                    "idioma": "Español",
                    "nivel": "Nativo"
                },
                {
                    "idioma": "Inglés",
                    "nivel": "C1 - Avanzado",
                    "certificacion": "C.A.B.S.I Escuela de Inglés"
                }
            ],
            
            "intereses_profesionales": [
                "Derecho Civil",
                "Derecho Comercial", 
                "Derecho Laboral",
                "Desarrollo profesional en el ámbito jurídico",
                "Experiencia práctica en diferentes sectores"
            ],
            
            "publicaciones": {
                "articulo_principal": {
                    "titulo": "Inteligencia Artificial y reconfiguración del Derecho: entre la opacidad, la responsabilidad y la precaución",
                    "revista": "IusTech Perú. Revista de Derecho y Tecnología",
                    "url": "https://latam.ijeditores.com/pop.php?option=articulo&Hash=8fbc818ddf5db16c359a53933c4d1368",
                    "areas": ["Inteligencia Artificial", "Derecho", "Tecnología", "Responsabilidad Legal"]
                }
            },
            
            "motivaciones": [
                "Aplicar conocimientos teóricos en entorno práctico",
                "Desarrollar experiencia profesional en el ámbito jurídico",
                "Contribuir al crecimiento de organizaciones",
                "Continuar aprendiendo y desarrollándose profesionalmente"
            ],
            
            "disponibilidad": {
                "horarios": "Flexible, compatible con horarios de estudio",
                "ubicacion": "CABA y alrededores",
                "modalidad": "Presencial o híbrida"
            }
            },
            
            "valentin": {
                "user_id": "valentin",
                "email": "valdom152@gmail.com",
                "nombre_completo": "Valentín Matías Domínguez Simonetti",
                "edad": 20,
                "ubicacion": "San Nicolás de los Arroyos / CABA",
                "telefono": "+5493364337508",
                "dni": "46.191.675",
                "fecha_nacimiento": "14 de Enero del 2005",
                "nacionalidad": "Argentina",
                
                "educacion": {
                    "carrera_principal": {
                        "titulo": "Abogacía",
                        "universidad": "Universidad de Buenos Aires - Facultad de Derecho",
                        "periodo": "Marzo 2024 - Actualidad",
                        "estado": "Cursando actualmente"
                    },
                    "educacion_previa": {
                        "cbc": {
                            "titulo": "Ciclo Básico Común (CBC) de Abogacía",
                            "institucion": "Universidad de Buenos Aires - Ciudad Universitaria",
                            "periodo": "Abril - Diciembre 2023"
                        },
                        "secundaria": {
                            "titulo": "Bachiller en Economía y Administración",
                            "institucion": "Colegio Nuestra Señora de la Misericordia",
                            "ubicacion": "San Nicolás de los Arroyos",
                            "periodo": "Marzo 2017 - Noviembre 2022"
                        }
                    }
                },
                
                "experiencia_laboral": [
                    {
                        "puesto": "Analista - Pasante",
                        "empresa": "Banco Patagonia S.A.",
                        "periodo": "2025",
                        "estado": "Actual",
                        "ubicaciones": [
                            "Avenida de Mayo 701, CABA",
                            "Sucursal Avenida Callao 273, CABA"
                        ],
                        "areas_rotacion": [
                            "Sector operaciones",
                            "Atención personas",
                            "Área de legales"
                        ],
                        "habilidades_desarrolladas": [
                            "Operaciones bancarias",
                            "Atención al cliente",
                            "Gestión legal bancaria",
                            "Trabajo en equipo",
                            "Adaptabilidad entre áreas"
                        ]
                    }
                ],
                
                "habilidades_tecnicas": [
                    "Operaciones bancarias",
                    "Atención al cliente",
                    "Administración",
                    "Economía básica",
                    "Gestión legal",
                    "Trabajo en equipo",
                    "Microsoft Office",
                    "Sistemas bancarios"
                ],
                
                "habilidades_blandas": [
                    "Respetuoso",
                    "Puntual",
                    "Trabajador en equipo",
                    "Responsable",
                    "Búsqueda constante de conocimiento",
                    "Nuevos aprendizajes",
                    "Adaptabilidad",
                    "Comunicación efectiva"
                ],
                
                "idiomas": [
                    {
                        "idioma": "Español",
                        "nivel": "Nativo"
                    },
                    {
                        "idioma": "Inglés",
                        "nivel": "Básico/Intermedio"
                    }
                ],
                
                "intereses_profesionales": [
                    "Derecho Bancario",
                    "Derecho Comercial",
                    "Economía y Administración",
                    "Operaciones financieras",
                    "Desarrollo profesional en el ámbito jurídico-financiero"
                ],
                
                "motivaciones": [
                    "Aplicar conocimientos teóricos en entorno práctico",
                    "Desarrollar experiencia en el sector legal",
                    "Contribuir al crecimiento de organizaciones",
                    "Continuar aprendiendo y desarrollándose profesionalmente",
                ],
                
                "disponibilidad": {
                    "horarios": "Flexible, compatible con horarios de estudio",
                    "ubicacion": "CABA y alrededores",
                    "modalidad": "Presencial o híbrida"
                }
            }
        }
    
    def analyze_job_offer(self, offer_data: Dict) -> Dict:
        """Analyze job offer to extract key information for personalization"""
        analysis = {
            "area": offer_data.get('area', ''),
            "company_type": self._infer_company_type(offer_data.get('area', '')),
            "salary": offer_data.get('asignacion_estimulo', ''),
            "schedule": offer_data.get('horario', ''),
            "requirements": self._extract_requirements(offer_data.get('descripcion_completa', '')),
            "key_skills": self._identify_relevant_skills(offer_data),
            "tone": self._determine_tone(offer_data.get('area', ''))
        }
        return analysis
    
    def _infer_company_type(self, area: str) -> str:
        """Infer company type from area description"""
        area_lower = area.lower()
        
        if 'igualdad' in area_lower or 'género' in area_lower:
            return 'área_universitaria'
        elif 'automobiles' in area_lower or 'fca' in area_lower:
            return 'empresa_automotriz'
        elif 'textil' in area_lower:
            return 'empresa_textil'
        elif 'big bang' in area_lower:
            return 'empresa_tecnologia'
        else:
            return 'empresa_general'
    
    def _extract_requirements(self, description: str) -> list:
        """Extract key requirements from job description"""
        requirements = []
        if not description:
            return requirements
        
        desc_lower = description.lower()
        
        # Common requirements patterns
        if 'promedio' in desc_lower:
            requirements.append('promedio_academico')
        if 'estudiante' in desc_lower:
            requirements.append('estudiante_activo')
        if 'horario' in desc_lower:
            requirements.append('disponibilidad_horaria')
        if 'experiencia' in desc_lower:
            requirements.append('experiencia_previa')
        
        return requirements
    
    def _identify_relevant_skills(self, offer_data: Dict) -> list:
        """Identify user skills relevant to the job offer"""
        relevant_skills = []
        area = offer_data.get('area', '').lower()
        description = offer_data.get('descripcion_completa', '').lower()
        
        # Map job areas to relevant user skills
        if 'atención' in description or 'cliente' in description:
            relevant_skills.extend(['Atención al cliente', 'Comunicación efectiva'])
        
        if 'administrativ' in description or 'administración' in description:
            relevant_skills.extend(['Microsoft Office', 'Organización'])
        
        if 'equipo' in description:
            relevant_skills.append('Trabajo en equipo')
        
        if 'presión' in description or 'demanda' in description:
            relevant_skills.append('Manejo de presión')
        
        # Always include basic skills
        relevant_skills.extend(['Responsabilidad', 'Puntualidad', 'Adaptabilidad'])
        
        return list(set(relevant_skills))  # Remove duplicates
    
    def _determine_tone(self, area: str) -> str:
        """Determine appropriate tone based on company/area"""
        area_lower = area.lower()
        
        if 'universidad' in area_lower or 'uba' in area_lower or 'académic' in area_lower:
            return 'académico_formal'
        elif 'automobiles' in area_lower or 'fca' in area_lower:
            return 'corporativo_profesional'
        elif 'textil' in area_lower:
            return 'empresarial_cercano'
        else:
            return 'profesional_equilibrado'
    
    def generate_personalized_email(self, offer_data: Dict, user_id: str = "damian") -> Dict:
        """Generate a personalized job application email using OpenAI"""
        
        # Get user profile
        user_profile = self.user_profiles.get(user_id)
        if not user_profile:
            raise ValueError(f"User profile not found: {user_id}")
        
        if not os.getenv('OPENAI_API_KEY'):
            logger.warning("OpenAI API key not configured")
            return self._generate_enhanced_template_email(offer_data, user_id)
        
        try:
            # Analyze the job offer
            analysis = self.analyze_job_offer(offer_data)
            
            # Create the prompt for OpenAI
            prompt = self._create_email_prompt(offer_data, analysis, user_profile)
            
            # Generate email with OpenAI
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # More cost-effective than gpt-4
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            email_content = response.choices[0].message.content.strip()
            
            numero = offer_data.get('numero_busqueda', offer_data.get('numero', ''))
            return {
                "subject": f"Postulación para Búsqueda N° {numero} - {user_profile['nombre_completo']}",
                "body": email_content,
                "success": True,
                "analysis": analysis,
                "generated_at": datetime.now().isoformat(),
                "user_id": user_id,
                "user_email": user_profile['email']
            }
            
        except Exception as e:
            logger.error(f"Error generating email with OpenAI: {e}")
            return self._generate_enhanced_template_email(offer_data, user_id)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for OpenAI"""
        return """Eres un experto en redacción profesional de cartas de presentación y emails de postulación laboral. 

Tu tarea es redactar emails profesionales, personalizados y efectivos para postulaciones a pasantías y trabajos.

INSTRUCCIONES:
- Sé profesional pero cercano
- Personaliza según la empresa y posición
- Destaca experiencias y habilidades relevantes
- Mantén un tono apropiado para el contexto
- Sé conciso pero completo (máximo 200 palabras)
- No incluyas saludos ni despedidas (solo el cuerpo del mensaje)
- Enfócate en el valor que el candidato puede aportar"""
    
    def _create_email_prompt(self, offer_data: Dict, analysis: Dict, user_profile: Dict) -> str:
        """Create the prompt for OpenAI email generation"""
        
        # Build education info
        education_info = f"{user_profile['educacion']['carrera_principal']['titulo']} - {user_profile['educacion']['carrera_principal']['estado']} en {user_profile['educacion']['carrera_principal']['universidad']}"
        
        # Build additional education info
        additional_education = ""
        if 'carrera_secundaria' in user_profile['educacion']:
            additional_education = f"- Formación adicional: {user_profile['educacion']['carrera_secundaria']['titulo']} ({user_profile['educacion']['carrera_secundaria']['institucion']})"
        elif 'educacion_previa' in user_profile['educacion']:
            prev_edu = user_profile['educacion']['educacion_previa']
            if 'cbc' in prev_edu:
                additional_education = f"- Formación previa: {prev_edu['cbc']['titulo']} en {prev_edu['cbc']['institucion']}"
            if 'secundaria' in prev_edu:
                additional_education += f"\n- Educación secundaria: {prev_edu['secundaria']['titulo']} - {prev_edu['secundaria']['institucion']}"
        
        # Build work experience info
        work_experience = ""
        if user_profile['experiencia_laboral']:
            for i, exp in enumerate(user_profile['experiencia_laboral'][:2]):  # Limit to first 2 experiences
                work_experience += f"  * {exp['puesto']} en {exp['empresa']} ({exp['periodo']})\n"
                if 'areas_rotacion' in exp:
                    work_experience += f"    Áreas: {', '.join(exp['areas_rotacion'])}\n"
        
        # Build skills info
        skills_info = ""
        if user_profile['experiencia_laboral'] and 'habilidades_desarrolladas' in user_profile['experiencia_laboral'][0]:
            skills_info = ', '.join(user_profile['experiencia_laboral'][0]['habilidades_desarrolladas'][:3])
        
        return f"""
INFORMACIÓN DEL CANDIDATO:
- Nombre: {user_profile['nombre_completo']}
- Edad: {user_profile['edad']} años
- Formación: {education_info}
{additional_education}
- Experiencia profesional: 
{work_experience}- Habilidades principales: {skills_info}
- Idiomas: {', '.join([f"{lang['idioma']} ({lang['nivel']})" for lang in user_profile['idiomas']])}
{f"- Publicación: Artículo sobre IA y Derecho en revista especializada" if user_profile.get('publicaciones') else ""}

OFERTA LABORAL:
- Búsqueda N°: {offer_data.get('numero_busqueda', '')}
- Área/Empresa: {offer_data.get('area', '')}
- Horario: {offer_data.get('horario', '')}
- Salario: ${offer_data.get('asignacion_estimulo', '')}
- Tipo de empresa: {analysis['company_type']}
- Tono recomendado: {analysis['tone']}
- Habilidades relevantes: {', '.join(analysis['key_skills'])}

CONTEXTO:
Esta es una postulación para una pasantía en la UBA Facultad de Derecho. El candidato es estudiante de Derecho con experiencia práctica relevante.

Redacta un email profesional de postulación que:
1. Mencione específicamente la búsqueda N° {offer_data.get('numero_busqueda', '')}
2. Destaque la experiencia y formación más relevante del candidato
3. Conecte las habilidades del candidato con los requerimientos
4. Muestre interés genuino en el área específica
5. Mencione disponibilidad horaria
6. Sea apropiado para el contexto ({analysis['tone']})
7. Personalice según el perfil del candidato

El email debe ser el cuerpo del mensaje únicamente (sin saludo inicial ni despedida final).
"""
    
    def _generate_enhanced_template_email(self, offer_data: Dict, user_id: str = "damian") -> Dict:
        """Generate a fallback email when OpenAI is not available"""
        
        user_profile = self.user_profiles.get(user_id)
        if not user_profile:
            raise ValueError(f"User profile not found: {user_id}")
        
        area = offer_data.get('area', 'la organización')
        numero = offer_data.get('numero_busqueda', '')
        horario = offer_data.get('horario', '')
        
        # Generate personalized template based on user profile
        if user_id == "damian":
            fallback_email = f"""Me dirijo a ustedes con el fin de postularme para la Búsqueda N° {numero} en {area}.

Soy estudiante de Abogacía en la Universidad de Buenos Aires, con experiencia práctica como paralegal en Estudio Arana desde 2021, donde me desempeño en redacción de escritos, contratos y apelaciones, procuración de expedientes y trámites ante organismos como IGJ y Colescba.

Actualmente me desempeño como Ayudante de Cátedra en Derechos Humanos y Garantías en la Facultad de Derecho de la UBA, dictando clases sobre IA y Derechos Humanos. Además, cuento con formación en Periodismo y nivel C1 de inglés, habiendo publicado artículos sobre Inteligencia Artificial y Derecho en revistas especializadas.

Mi experiencia jurídica práctica, combinada con mi formación académica y habilidades de comunicación, me posicionan como un candidato idóneo para contribuir efectivamente al equipo. Tengo amplio manejo de sistemas jurídicos como PJN, SCBA, Lex Doctor, entre otros.

Tengo disponibilidad horaria {horario.lower() if horario else 'flexible'} y gran interés en aplicar mis conocimientos y experiencia en un entorno profesional diverso."""
        
        elif user_id == "valentin":
            fallback_email = f"""Me dirijo a ustedes con el fin de postularme para la Búsqueda N° {numero} en {area}.

Soy estudiante de Abogacía en la Universidad de Buenos Aires (desde marzo 2024), habiendo completado el CBC en Ciudad Universitaria en 2023. Cuento con formación secundaria en Economía y Administración del Colegio Nuestra Señora de la Misericordia.

Actualmente me desempeño como Analista/Pasante en Banco Patagonia S.A., rotando por diferentes áreas: operaciones, atención a personas y área legal. Esta experiencia me ha permitido desarrollar habilidades en operaciones bancarias, atención al cliente y gestión legal, así como adaptabilidad para trabajar en diferentes entornos.

Mi combinación de formación jurídica en curso, experiencia práctica en el sector financiero-legal y sólida base en economía y administración me posicionan como un candidato comprometido para contribuir al equipo. Poseo habilidades en Microsoft Office, sistemas bancarios y manejo de situaciones diversas.

Tengo disponibilidad horaria {horario.lower() if horario else 'flexible, compatible con mis estudios'} y gran interés en aplicar mis conocimientos y seguir desarrollándome profesionalmente en el ámbito jurídico."""
        
        else:
            # Generic template for unknown users
            fallback_email = f"""Me dirijo a ustedes con el fin de postularme para la Búsqueda N° {numero} en {area}.

Soy estudiante de {user_profile['educacion']['carrera_principal']['titulo']} en {user_profile['educacion']['carrera_principal']['universidad']}, con gran interés en desarrollarme profesionalmente en el ámbito jurídico.

Tengo disponibilidad horaria {horario.lower() if horario else 'flexible'} y gran motivación para contribuir al equipo.

Quedo a disposición para ampliar cualquier información que consideren necesaria y agradezco la oportunidad de ser considerado para esta posición."""

        return {
            "subject": f"Postulación para Búsqueda N° {numero} - {user_profile['nombre_completo']}",
            "body": fallback_email,
            "success": True,
            "analysis": {"note": "Generated using enhanced template (OpenAI not available)"},
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "user_email": user_profile['email']
        }
    
    def create_mailto_link(self, email_address: str, offer_data: Dict) -> str:
        """Create a mailto link with AI-generated content"""
        
        # Generate the personalized email
        email_result = self.generate_personalized_email(offer_data)
        
        if not email_result["success"]:
            logger.error("Failed to generate email content")
            return f"mailto:{email_address}?subject=Postulación Búsqueda N° {offer_data.get('numero_busqueda', '')}"
        
        # URL encode the email body for mailto link
        import urllib.parse
        
        subject = urllib.parse.quote(email_result["subject"])
        body = urllib.parse.quote(email_result["body"])
        
        mailto_link = f"mailto:{email_address}?subject={subject}&body={body}"
        
        return mailto_link
    
    def get_user_emails(self) -> Dict[str, str]:
        """Get all user emails mapped to their user IDs"""
        return {user_id: profile['email'] for user_id, profile in self.user_profiles.items()}
    
    def get_user_name(self, user_id: str) -> str:
        """Get user's full name by user ID"""
        profile = self.user_profiles.get(user_id)
        return profile['nombre_completo'] if profile else "Usuario desconocido"

def test_ai_agent():
    """Test the AI agent with sample data"""
    
    # Sample offer data (like the new offers you received)
    sample_offer = {
        "numero_busqueda": "3366",
        "area": "Industria Textil Cladd",
        "horario": "9 a 13 hs",
        "asignacion_estimulo": "500.000",
        "contacto_email": "rodrigo@cladd.com.ar",
        "descripcion_completa": "Búsqueda para estudiante de derecho con buen promedio académico para tareas administrativas y atención al cliente en empresa textil..."
    }
    
    # Initialize AI agent
    agent = AIJobApplicationAgent()
    
    # Generate email
    print("🤖 Testing AI Agent...")
    result = agent.generate_personalized_email(sample_offer)
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📧 Subject: {result['subject']}")
    print(f"\n📝 Email Body:\n{result['body']}")
    
    # Test mailto link
    mailto_link = agent.create_mailto_link("rodrigo@cladd.com.ar", sample_offer)
    print(f"\n🔗 Mailto Link: {mailto_link[:100]}...")

if __name__ == "__main__":
    test_ai_agent()