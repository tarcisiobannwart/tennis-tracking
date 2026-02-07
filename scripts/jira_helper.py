#!/usr/bin/env python3
"""
Jira Helper Script - Tennis Tracking

Script utilitario para operacoes com o Jira via API REST.
Usado pelo Claude Code para criar, buscar e atualizar issues.

Uso:
    python scripts/jira_helper.py search "project = TT"
    python scripts/jira_helper.py get TT-123
    python scripts/jira_helper.py create --type Bug --summary "Titulo" --description "Descricao"
    python scripts/jira_helper.py transition TT-123 21  # 21=In Progress, 32=Review, 41=Done
    python scripts/jira_helper.py comment TT-123 "Comentario"
    python scripts/jira_helper.py attach TT-123 /path/to/file.png  # Anexar arquivo
    python scripts/jira_helper.py pending  # Listar issues pendentes
"""

import urllib.request
import urllib.parse
import base64
import json
import sys
import argparse

# Configuracao do Jira
JIRA_EMAIL = "tarcisio@trademarketingforce.com"
JIRA_TOKEN = ""
JIRA_BASE_URL = "https://trademarketingforce.atlassian.net"
PROJECT_KEY = "TT"


def get_auth_header():
    """Gera o header de autenticacao Basic."""
    credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    return f"Basic {credentials}"


def make_request(endpoint, method="GET", data=None):
    """Faz uma requisicao para a API do Jira."""
    url = f"{JIRA_BASE_URL}{endpoint}"
    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, headers=headers, method=method)

    if data:
        req.data = json.dumps(data).encode()

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return {"success": True}
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_data = json.loads(error_body)
        except:
            error_data = {"message": error_body[:500]}
        return {"error": True, "status": e.code, "data": error_data}


def search_issues(jql, max_results=20):
    """Busca issues usando JQL (nova API)."""
    encoded_jql = urllib.parse.quote(jql)
    endpoint = f"/rest/api/3/search/jql?jql={encoded_jql}&maxResults={max_results}&fields=summary,status,issuetype,priority,assignee,description,created,labels,customfield_10016"

    result = make_request(endpoint)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return []

    return result.get("issues", [])


def get_issue(issue_key):
    """Busca uma issue especifica."""
    endpoint = f"/rest/api/3/issue/{issue_key}"
    result = make_request(endpoint)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return None

    return result


def create_issue(issue_type, summary, description, priority="Medium", labels=None, parent=None):
    """Cria uma nova issue."""
    endpoint = "/rest/api/3/issue"

    # Construir descricao em formato ADF (Atlassian Document Format)
    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": description}]
            }
        ]
    }

    data = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": description_adf,
            "issuetype": {"name": issue_type},
            "priority": {"name": priority}
        }
    }

    if labels:
        data["fields"]["labels"] = labels

    if parent:
        data["fields"]["parent"] = {"key": parent}

    result = make_request(endpoint, method="POST", data=data)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return None

    return result


def transition_issue(issue_key, transition_id):
    """Transiciona uma issue para outro status."""
    endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
    data = {"transition": {"id": str(transition_id)}}

    result = make_request(endpoint, method="POST", data=data)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return False

    return True


def add_comment(issue_key, comment_text):
    """Adiciona um comentario a uma issue."""
    endpoint = f"/rest/api/3/issue/{issue_key}/comment"

    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": comment_text}]
                }
            ]
        }
    }

    result = make_request(endpoint, method="POST", data=data)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return False

    return True


def get_transitions(issue_key):
    """Lista transicoes disponiveis para uma issue."""
    endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
    result = make_request(endpoint)

    if "error" in result:
        print(f"Erro: {result['status']} - {result['data']}", file=sys.stderr)
        return []

    return result.get("transitions", [])


def attach_file(issue_key, file_path):
    """Anexa um arquivo a uma issue."""
    import os
    import mimetypes

    if not os.path.exists(file_path):
        print(f"Erro: Arquivo nao encontrado: {file_path}", file=sys.stderr)
        return False

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments"
    filename = os.path.basename(file_path)

    # Detectar tipo MIME
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Criar boundary para multipart
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    # Ler conteudo do arquivo
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Construir body multipart
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()

    # Headers especificos para upload
    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "X-Atlassian-Token": "no-check"
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Erro ao anexar arquivo: {e.code} - {error_body[:500]}", file=sys.stderr)
        return False


def format_issue(issue):
    """Formata uma issue para exibicao."""
    fields = issue.get("fields", {})
    return {
        "key": issue.get("key"),
        "summary": fields.get("summary", ""),
        "status": fields.get("status", {}).get("name", ""),
        "type": fields.get("issuetype", {}).get("name", ""),
        "priority": fields.get("priority", {}).get("name", ""),
        "assignee": fields.get("assignee", {}).get("displayName", "Nao atribuido") if fields.get("assignee") else "Nao atribuido",
        "created": fields.get("created", "")[:10],
        "labels": fields.get("labels", []),
        "story_points": fields.get("customfield_10016"),
    }


def main():
    parser = argparse.ArgumentParser(description="Jira Helper - Tennis Tracking")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponiveis")

    # Comando search
    search_parser = subparsers.add_parser("search", help="Buscar issues com JQL")
    search_parser.add_argument("jql", help="Query JQL")
    search_parser.add_argument("--max", type=int, default=20, help="Maximo de resultados")
    search_parser.add_argument("--json", action="store_true", help="Saida em JSON")

    # Comando get
    get_parser = subparsers.add_parser("get", help="Buscar issue especifica")
    get_parser.add_argument("key", help="Chave da issue (ex: TT-123)")
    get_parser.add_argument("--json", action="store_true", help="Saida em JSON")

    # Comando create
    create_parser = subparsers.add_parser("create", help="Criar nova issue")
    create_parser.add_argument("--type", required=True, help="Tipo (Tarefa, Epic, Subtask)")
    create_parser.add_argument("--summary", required=True, help="Titulo da issue")
    create_parser.add_argument("--description", default="", help="Descricao")
    create_parser.add_argument("--priority", default="Medium", help="Prioridade (Highest, High, Medium, Low, Lowest)")
    create_parser.add_argument("--labels", help="Labels separadas por virgula")
    create_parser.add_argument("--parent", help="Issue pai (para Subtask)")
    create_parser.add_argument("--json", action="store_true", help="Saida em JSON")

    # Comando transition
    trans_parser = subparsers.add_parser("transition", help="Transicionar issue")
    trans_parser.add_argument("key", help="Chave da issue")
    trans_parser.add_argument("transition_id", help="ID da transicao (21=InProgress, 32=Review, 41=Done)")

    # Comando comment
    comment_parser = subparsers.add_parser("comment", help="Adicionar comentario")
    comment_parser.add_argument("key", help="Chave da issue")
    comment_parser.add_argument("text", help="Texto do comentario")

    # Comando transitions (listar transicoes disponiveis)
    list_trans_parser = subparsers.add_parser("transitions", help="Listar transicoes disponiveis")
    list_trans_parser.add_argument("key", help="Chave da issue")

    # Comando pending (issues pendentes)
    pending_parser = subparsers.add_parser("pending", help="Listar issues pendentes")
    pending_parser.add_argument("--max", type=int, default=10, help="Maximo de resultados")
    pending_parser.add_argument("--json", action="store_true", help="Saida em JSON")

    # Comando attach (anexar arquivo)
    attach_parser = subparsers.add_parser("attach", help="Anexar arquivo a uma issue")
    attach_parser.add_argument("key", help="Chave da issue (ex: TT-123)")
    attach_parser.add_argument("file", help="Caminho do arquivo para anexar")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        issues = search_issues(args.jql, args.max)
        if args.json:
            print(json.dumps([format_issue(i) for i in issues], indent=2, ensure_ascii=False))
        else:
            for issue in issues:
                i = format_issue(issue)
                print(f"[{i['key']}] ({i['status']}) {i['type']} - {i['priority']}")
                print(f"  {i['summary']}")
                print()

    elif args.command == "get":
        issue = get_issue(args.key)
        if issue:
            if args.json:
                print(json.dumps(issue, indent=2, ensure_ascii=False))
            else:
                i = format_issue(issue)
                print(f"=== {i['key']} ===")
                print(f"Tipo: {i['type']}")
                print(f"Status: {i['status']}")
                print(f"Prioridade: {i['priority']}")
                print(f"Atribuido: {i['assignee']}")
                print(f"Resumo: {i['summary']}")
                print(f"Criado: {i['created']}")

    elif args.command == "create":
        labels = args.labels.split(",") if args.labels else None
        result = create_issue(
            args.type,
            args.summary,
            args.description,
            args.priority,
            labels,
            args.parent
        )
        if result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Issue criada: {result.get('key')}")
                print(f"   URL: {JIRA_BASE_URL}/browse/{result.get('key')}")

    elif args.command == "transition":
        if transition_issue(args.key, args.transition_id):
            print(f"{args.key} transicionada com sucesso")
        else:
            print(f"Erro ao transicionar {args.key}")
            sys.exit(1)

    elif args.command == "comment":
        if add_comment(args.key, args.text):
            print(f"Comentario adicionado em {args.key}")
        else:
            print(f"Erro ao comentar em {args.key}")
            sys.exit(1)

    elif args.command == "transitions":
        transitions = get_transitions(args.key)
        print(f"Transicoes disponiveis para {args.key}:")
        for t in transitions:
            print(f"  ID: {t['id']} - {t['name']}")

    elif args.command == "pending":
        jql = f"project = {PROJECT_KEY} AND status NOT IN (Done, Review) ORDER BY priority DESC, created ASC"
        issues = search_issues(jql, args.max)
        if args.json:
            print(json.dumps([format_issue(i) for i in issues], indent=2, ensure_ascii=False))
        else:
            print(f"{len(issues)} issues pendentes no {PROJECT_KEY}:\n")
            for issue in issues:
                i = format_issue(issue)
                print(f"[{i['key']}] ({i['status']}) {i['type']} - {i['priority']}")
                print(f"  {i['summary']}")
                print()

    elif args.command == "attach":
        result = attach_file(args.key, args.file)
        if result:
            print(f"Arquivo anexado com sucesso em {args.key}")
            if isinstance(result, list) and len(result) > 0:
                print(f"   ID: {result[0].get('id')}")
                print(f"   Nome: {result[0].get('filename')}")
        else:
            print(f"Erro ao anexar arquivo em {args.key}")
            sys.exit(1)


if __name__ == "__main__":
    main()
