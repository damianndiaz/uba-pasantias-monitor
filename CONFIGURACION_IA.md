# Configuración del Sistema UBA Pasantías Monitor con IA

## Configuración de OpenAI API Key

Para usar las funciones de IA, necesitas configurar tu API key de OpenAI:

### Opción 1: Variable de Entorno (Recomendado)
```bash
set OPENAI_API_KEY=tu_api_key_aqui
```

### Opción 2: En config.json
```json
{
  "ai_settings": {
    "openai_api_key": "tu_api_key_aqui",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

## Obtener API Key de OpenAI

1. Ve a https://platform.openai.com/
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" en tu panel
4. Crea una nueva API key
5. Copia la clave y úsala en la configuración

## Características de la IA

- **Emails Personalizados**: Genera emails de aplicación personalizados basados en tu perfil profesional
- **Análisis de Ofertas**: Analiza cada oferta para crear contenido relevante
- **Múltiples Opciones**: Botón con IA personalizada + botón de email simple
- **Vista Previa**: Muestra una preview del email generado por IA en el notification

## Funcionalidad sin OpenAI

Si no configuras OpenAI, el sistema seguirá funcionando pero:
- Los emails de aplicación serán simples (sin personalización IA)
- No habrá vista previa del contenido generado
- Solo aparecerá el botón de "Email Simple"

## Perfil de Usuario Incluido

El sistema incluye tu perfil profesional basado en tu CV:
- Damián Gonzalo Díaz
- Estudiante de 4to año de Derecho (UBA)  
- Experiencia en McDonald's (atención al cliente)
- Idiomas: Español nativo, Inglés intermedio
- Intereses en derecho comercial y corporativo

Este perfil se usa para personalizar los emails de aplicación automáticamente.