from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent.browser import Browser

TOOLS_OPENAI: list[dict[str, Any]] = [
    # ── Navigation ──────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navega para uma URL e aguarda o carregamento completo",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_navigate_back",
            "description": "Volta para a página anterior no histórico do navegador",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_navigate_forward",
            "description": "Avança para a próxima página no histórico do navegador",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_reload",
            "description": "Recarrega a página atual",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_url",
            "description": "Retorna a URL atual da página",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Snapshot / Inspection ────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_snapshot",
            "description": (
                "Retorna a árvore de acessibilidade da página (elementos, roles, nomes). "
                "Use após cada ação para entender o estado da tela."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_inputs",
            "description": (
                "Retorna todos os campos de input visíveis com seus atributos reais "
                "(id, name, type, placeholder, label). "
                "Use SEMPRE antes de preencher qualquer campo para descobrir o seletor correto."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_text",
            "description": "Retorna o texto visível da página (útil para checar mensagens ou confirmar navegação)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_html",
            "description": "Retorna o HTML interno de um seletor CSS para inspecionar a estrutura dos elementos",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Seletor CSS (padrão: 'body')"}
                },
            },
        },
    },
    # ── Frames ───────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_get_frames",
            "description": (
                "Lista todos os frames/iframes presentes na página com index, name e URL. "
                "Use para descobrir qual frame acessar antes de chamar browser_switch_frame."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_switch_frame",
            "description": (
                "Muda o contexto ativo para um iframe. Após isso, todos os tools de interação "
                "(click, fill, snapshot etc.) operam dentro do frame selecionado. "
                "Identifique o frame pelo index (retornado por browser_get_frames), name ou url_contains."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Index do frame (0 = frame principal)",
                    },
                    "name": {"type": "string", "description": "Atributo name/id do iframe no HTML"},
                    "url_contains": {
                        "type": "string",
                        "description": "Trecho da URL do frame para busca parcial",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_switch_main_frame",
            "description": "Volta o contexto ativo para o frame principal da página (saindo de qualquer iframe)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_console_messages",
            "description": "Retorna as mensagens do console do navegador (logs, erros, warnings)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Interaction ──────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Clica em um elemento. Ex: 'text=Login', '#btn-submit', 'input[type=submit]'",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_fill",
            "description": "Preenche um campo limpando o conteúdo antes. Use o seletor exato retornado por browser_get_inputs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["selector", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_type",
            "description": "Digita texto caractere por caractere em um campo (útil quando fill() ignora eventos de input)",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "text": {"type": "string"},
                    "delay": {
                        "type": "integer",
                        "description": "Delay em ms entre teclas (padrão: 0)",
                        "default": 0,
                    },
                },
                "required": ["selector", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_press_key",
            "description": "Pressiona uma tecla. Ex: 'Enter', 'Tab', 'Escape', 'ArrowDown'",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_fill_form",
            "description": (
                "Preenche múltiplos campos de formulário em uma única chamada. "
                "Suporta fill (texto), select (dropdown), check e uncheck (checkbox/radio). "
                "Use browser_get_inputs antes para descobrir os seletores corretos."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "array",
                        "description": "Lista de campos a preencher",
                        "items": {
                            "type": "object",
                            "properties": {
                                "selector": {
                                    "type": "string",
                                    "description": "Seletor CSS do campo",
                                },
                                "value": {
                                    "type": "string",
                                    "description": "Valor a preencher/selecionar (não usado em check/uncheck)",
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["fill", "select", "check", "uncheck"],
                                    "description": "Ação a executar (padrão: fill)",
                                    "default": "fill",
                                },
                            },
                            "required": ["selector"],
                        },
                    }
                },
                "required": ["fields"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_check",
            "description": "Marca um checkbox ou radio button",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_uncheck",
            "description": "Desmarca um checkbox",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_hover",
            "description": "Move o mouse sobre um elemento (útil para abrir menus dropdown ou tooltips)",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_select_option",
            "description": "Seleciona uma opção em um elemento <select> pelo valor, label ou index",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Seletor CSS do <select>"},
                    "value": {
                        "type": "string",
                        "description": "Valor, texto visível ou index da opção",
                    },
                },
                "required": ["selector", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_drag",
            "description": "Arrasta um elemento e solta em outro (drag and drop)",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_selector": {
                        "type": "string",
                        "description": "Seletor CSS do elemento a arrastar",
                    },
                    "target_selector": {"type": "string", "description": "Seletor CSS do destino"},
                },
                "required": ["source_selector", "target_selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_file_upload",
            "description": "Faz upload de arquivos em um input[type=file]",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "Seletor CSS do input[type=file]",
                    },
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de caminhos absolutos dos arquivos a enviar",
                    },
                },
                "required": ["selector", "paths"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_scroll",
            "description": "Rola a página ou rola até um elemento específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "Direção de rolagem (ignorado se 'selector' for fornecido)",
                        "default": "down",
                    },
                    "amount": {
                        "type": "integer",
                        "description": "Pixels a rolar (padrão: 300)",
                        "default": 300,
                    },
                    "selector": {
                        "type": "string",
                        "description": "Se fornecido, rola até o elemento ficar visível",
                    },
                },
            },
        },
    },
    # ── JavaScript ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_evaluate",
            "description": "Executa JavaScript na página e retorna o resultado. Use para ler dados, manipular DOM ou checar estado da aplicação.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "Expressão ou função JS a executar"}
                },
                "required": ["script"],
            },
        },
    },
    # ── Dialogs ──────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_handle_dialog",
            "description": (
                "Configura um handler para o próximo diálogo do navegador (alert, confirm, prompt). "
                "Chame ANTES da ação que vai disparar o diálogo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "accept": {
                        "type": "boolean",
                        "description": "true para aceitar/OK, false para cancelar/dismiss",
                        "default": True,
                    },
                    "prompt_text": {
                        "type": "string",
                        "description": "Texto a inserir em diálogos prompt (ignorado para alert/confirm)",
                        "default": "",
                    },
                },
            },
        },
    },
    # ── Flow control ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "task_complete",
            "description": (
                "Chame esta ferramenta EXATAMENTE UMA VEZ quando tiver executado com sucesso "
                "todos os passos do fluxo descrito. Após isso o sistema pedirá que você gere "
                "os arquivos de código — não use mais nenhuma outra ferramenta de browser."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Screenshot ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_take_screenshot",
            "description": "Tira um screenshot da página atual e salva em arquivo",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Caminho do arquivo de saída (padrão: screenshot.png)",
                        "default": "screenshot.png",
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "true para capturar a página inteira (padrão: false)",
                        "default": False,
                    },
                },
            },
        },
    },
    # ── Misc ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "browser_wait",
            "description": "Aguarda N milissegundos (use quando animações ou dropdowns precisam terminar)",
            "parameters": {
                "type": "object",
                "properties": {"milliseconds": {"type": "integer", "default": 1000}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_resize",
            "description": "Redimensiona a janela do navegador para as dimensões especificadas",
            "parameters": {
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "Largura em pixels"},
                    "height": {"type": "integer", "description": "Altura em pixels"},
                },
                "required": ["width", "height"],
            },
        },
    },
]

TOOLS_ANTHROPIC = [
    {
        "name": t["function"]["name"],
        "description": t["function"]["description"],
        "input_schema": t["function"].get("parameters", {"type": "object", "properties": {}}),
    }
    for t in TOOLS_OPENAI
]


async def _noop() -> str:
    return "ok"


async def call_tool(browser: "Browser", name: str, args: dict, output_dir: Path = Path(".")) -> str:
    try:
        dispatch = {
            # Navigation
            "browser_navigate": lambda: browser.navigate(args["url"]),
            "browser_navigate_back": lambda: browser.navigate_back(),
            "browser_navigate_forward": lambda: browser.navigate_forward(),
            "browser_reload": lambda: browser.reload(),
            "browser_get_url": lambda: browser.get_url(),
            # Frames
            "browser_get_frames": lambda: browser.get_frames(),
            "browser_switch_frame": lambda: browser.switch_frame(
                args.get("index"),
                args.get("name"),
                args.get("url_contains"),
            ),
            "browser_switch_main_frame": lambda: browser.switch_main_frame(),
            # Snapshot / Inspection
            "browser_snapshot": lambda: browser.snapshot(),
            "browser_get_inputs": lambda: browser.get_inputs(),
            "browser_get_text": lambda: browser.get_text(),
            "browser_get_html": lambda: browser.get_html(args.get("selector", "body")),
            "browser_get_console_messages": lambda: browser.get_console_messages(),
            # Interaction
            "browser_click": lambda: browser.click(args["selector"]),
            "browser_fill": lambda: browser.fill(args["selector"], args["value"]),
            "browser_fill_form": lambda: browser.fill_form(args["fields"]),
            "browser_check": lambda: browser.check(args["selector"]),
            "browser_uncheck": lambda: browser.uncheck(args["selector"]),
            "browser_type": lambda: browser.type_text(
                args["selector"], args["text"], args.get("delay", 0)
            ),
            "browser_press_key": lambda: browser.press_key(args["key"]),
            "browser_hover": lambda: browser.hover(args["selector"]),
            "browser_select_option": lambda: browser.select_option(args["selector"], args["value"]),
            "browser_drag": lambda: browser.drag(args["source_selector"], args["target_selector"]),
            "browser_file_upload": lambda: browser.file_upload(args["selector"], args["paths"]),
            "browser_scroll": lambda: browser.scroll(
                args.get("direction", "down"),
                args.get("amount", 300),
                args.get("selector", ""),
            ),
            # JavaScript
            "browser_evaluate": lambda: browser.evaluate(args["script"]),
            # Dialogs
            "browser_handle_dialog": lambda: browser.handle_dialog(
                args.get("accept", True),
                args.get("prompt_text", ""),
            ),
            # Flow control
            "task_complete": lambda: _noop(),
            # Screenshot — always saved inside output_dir/screenshots/
            "browser_take_screenshot": lambda: browser.take_screenshot(
                str(output_dir / "screenshots" / Path(args.get("path", "screenshot.png")).name),
                args.get("full_page", False),
            ),
            # Misc
            "browser_wait": lambda: browser.wait(args.get("milliseconds", 1000)),
            "browser_resize": lambda: browser.resize(args["width"], args["height"]),
        }
        if name in dispatch:
            return await dispatch[name]()
        return f"Ferramenta desconhecida: {name}"
    except Exception as exc:
        return f"Erro em {name}: {exc}"
