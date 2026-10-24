"""Read-only provider availability check; never prints credentials or error bodies."""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path


def probe():
    key=os.environ.get('OPENAI_API_KEY')
    configured=os.environ.get('GHOSTTRACE_AI_MODEL','')
    if not key: return {'provider':'OpenAI','available':False,'reason':'no environment credential','inference_calls':0}
    req=urllib.request.Request('https://api.openai.com/v1/models',headers={'Authorization':'Bearer '+key})
    try:
        with urllib.request.urlopen(req,timeout=15) as response: data=json.load(response)
        models=sorted(r['id'] for r in data['data'])
        preferred=[m for m in models if m.startswith('gpt-') and any(part in m for part in ('mini','nano'))]
        return {'provider':'OpenAI','available':True,'configured_model':configured or None,
                'configured_model_advertised':configured in models,'small_text_models':preferred,'inference_calls':0}
    except urllib.error.HTTPError as error:
        return {'provider':'OpenAI','available':False,'reason':f'HTTP {error.code}','inference_calls':0}
    except (urllib.error.URLError,OSError,TimeoutError):
        return {'provider':'OpenAI','available':False,'reason':'transport unavailable','inference_calls':0}


if __name__=='__main__':
    result=probe()
    output=Path(__file__).resolve().parents[1]/'artifacts/ai_access_probe.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
