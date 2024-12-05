from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.contrib import messages
from django.shortcuts import redirect
from .models import agendamento
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Maquina
from django.shortcuts import render, get_object_or_404
from .models import Funcionario
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.db.models import Q  # Importando Q para criar consultas mais complexas



def listar_maquinas(request):
    search_query = request.GET.get('search', '')  # Pega o valor da busca
    if search_query:
        # Filtra as máquinas com base no nome, tipo de máquina, tipo de manutenção ou descrição
        easy_maquinas = Maquina.objects.filter(
            Q(nome__icontains=search_query) |
            Q(tipomaq__icontains=search_query) |
            Q(tipomanu__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )
    else:
        # Se não houver busca, traz todas as máquinas
        easy_maquinas = Maquina.objects.all()

    # Paginação
    paginator = Paginator(easy_maquinas, 10)  # 10 máquinas por página
    page_number = request.GET.get('page')  # Pega o número da página
    page_obj = paginator.get_page(page_number)  # Pega a página solicitada

    return render(request, 'easy/tabelasmaquinas.html', {'page_obj': page_obj, 'search': search_query})


def lista_funcionarios(request):
    search = request.GET.get('search', '')  # Pega o parâmetro de pesquisa (se houver)

    # Filtra os funcionários pelo nome
    if search:
        funcionarios = Funcionario.objects.filter(
            nome__icontains=search)  # Filtrando os nomes que contêm a string pesquisada
    else:
        funcionarios = Funcionario.objects.all()  # Se não houver pesquisa, exibe todos

    # Paginação (opcional)
    from django.core.paginator import Paginator
    paginator = Paginator(funcionarios, 10)  # Exibe 10 funcionários por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'easy/tabelafuncionarios.html', {'search': search, 'page_obj': page_obj})
def excluir_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    funcionario.delete()
    messages.success(request, 'Funcionário excluído com sucesso.')
    return redirect('tabela_funcionario')


def editar_funcionario(request, id):
    funcionario = get_object_or_404(Funcionario, id=id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        senha = request.POST.get('senha')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')

        print(nome, sobrenome, senha, cpf, telefone)  # Verifique se os dados estão sendo enviados

        funcionario.nome = nome
        funcionario.sobrenome = sobrenome
        funcionario.senha = senha
        funcionario.cpf = cpf
        funcionario.telefone = telefone
        funcionario.save()

        return redirect('tabela_funcionario')
    return render(request, 'easy/editar_funcionario.html', {'funcionario': funcionario})


def tabelas_view(request):
    funcionarios = Funcionario.objects.all()  # Busca todos os funcionários

    # Criação do paginator com 10 itens por página
    paginator = Paginator(funcionarios, 10)

    # Obtém o número da página a partir da query string, se houver
    page_number = request.GET.get('page')

    # Pega a página especificada
    page_obj = paginator.get_page(page_number)

    return render(request, 'easy/tabelafuncionarios.html', {'page_obj': page_obj})


def maquinas_view(request):
        maquinas = Maquina.objects.all()
        return render(request, 'easy/tabelasmaquinas.html', {'maquinas': maquinas})


def excluir_maquina(request, id):
    maquina = get_object_or_404(Maquina, id=id)
    maquina.delete()  # Exclui a máquina do banco de dados
    return redirect('tabela_maquina')

def editar_maquina(request, id):
    maquina = get_object_or_404(Maquina, id=id)

    if request.method == 'POST':
        maquina.nome = request.POST.get('nome')
        maquina.tipomaq = request.POST.get('tipomaq')
        maquina.tipomanu = request.POST.get('tipomanu')
        maquina.descricao = request.POST.get('descricao')
        if request.FILES.get('imagem'):
            maquina.imagem = request.FILES.get('imagem')
        maquina.save()  # Salva as alterações

        return redirect('tabela_maquina')  # Redireciona para a tabela após a edição

    return render(request, 'easy/editar_maquina.html', {'maquina': maquina})


@csrf_exempt
def atualizar_status_maquina(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            novo_status = data.get('status')
            maquina = Maquina.objects.get(id=id)
            maquina.status = novo_status  # Adicione um campo 'status' no modelo se ainda não tiver
            maquina.save()
            return JsonResponse({'message': 'Status atualizado com sucesso!'}, status=200)
        except Maquina.DoesNotExist:
            return JsonResponse({'error': 'Máquina não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def obter_eventos(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    eventos_list = []

    if month and year:
        eventos = agendamento.objects.filter(dia__month=month, dia__year=year)
        eventos_list = [{'dia': evento.dia.strftime('%Y-%m-%d'), 'nome': evento.nome, 'tipomanu': evento.tipomanu} for evento in eventos]

    return JsonResponse(eventos_list, safe=False)


# Login ADMIN
USUARIO_FIXO = 'Admin'
SENHA_FIXA = '@801'

def login_admin(request):
    global usuarioLogado
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == USUARIO_FIXO and password == SENHA_FIXA:
            usuarioLogado = username
            return redirect('menuadmin')  # Redireciona após o login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'easy/loginadmin.html')


# Login Docente
# Login Docente
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('nome')  # O nome do usuário
        password = request.POST.get('senha')  # A senha fornecida

        print(f"Username: {username}")

        if not username or not password:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, 'easy/logindocente.html')

        try:
            # Buscar no banco de dados usando o nome de usuário fornecido
            with connection.cursor() as cursor:
                cursor.execute("SELECT senha FROM easy_funcionario WHERE LOWER(nome) = LOWER(%s)", [username])
                result = cursor.fetchone()

            if result:
                # Se o usuário for encontrado, obter a senha criptografada
                senha_ofc = result[0]  # result[0] é a senha armazenada no banco de dados

                # Verificar se a senha fornecida corresponde à senha criptografada
                if check_password(password, senha_ofc):  # Usando check_password para verificar a senha
                    messages.success(request, "Login bem-sucedido!")
                    return redirect('menu')  # Redirecionar para a página inicial após o login bem-sucedido
                else:
                    # Se a senha não for compatível
                    print(f"Senha fornecida: {password}")
                    print(f"Senha armazenada : {senha_ofc}")
                    messages.error(request, "Senha incorreta!")  # Senha não confere
            else:
                messages.error(request, 'Usuário inexistente ou senha inválida.')  # Usuário não encontrado

        except Exception as e:
            print(f"Erro ao acessar o banco de dados: {e}")
            messages.error(request, "Erro ao processar sua solicitação. Tente novamente mais tarde.")

    return render(request, 'easy/logindocente.html')  # Renderiza o template de login
# Função responsável pelo formulário de docente
usuarioLogado = None  # Defina um valor padrão

def cadastrar_usuario(request):
    global usuarioLogado
    if request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')

        # Criptografar a senha antes de salvar no banco
        senha_criptografada = make_password(senha)

        try:
            # Usando o ORM do Django para salvar o funcionário
            Funcionario.objects.create(
                nome=nome,
                sobrenome=sobrenome,
                cpf=cpf,
                telefone=telefone,
                senha=senha_criptografada  # Senha criptografada
            )
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('cadastrar_usuario')
        except Exception as e:
            messages.error(request, f'Erro ao realizar o cadastro: {e}')

    return render(request, 'easy/cadastrar_funcionarios.html', {'usuarioLogado': usuarioLogado})
# Função responsável pelo formílário de Máquinas
def cadastrar_maquina(request):
    global usuarioLogado

    # Inicializa 'usuarioLogado' se não estiver definido
    if 'usuarioLogado' not in globals() or not usuarioLogado:
        usuarioLogado = 'Desconhecido'  # ou outro valor padrão

    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipomaq = request.POST.get('tipomaq')
        tipomanu = request.POST.get('tipomanu')
        descricao = request.POST.get('descricao')
        imagem = request.FILES.get('imagem')

        try:
            # Salva a imagem usando o sistema de arquivos do Django
            if imagem:
                imagem_nome = default_storage.save(imagem.name, ContentFile(imagem.read()))

            Maquina.objects.create(
                nome=nome,
                tipomaq=tipomaq,
                tipomanu=tipomanu,
                descricao=descricao,
                imagem=imagem_nome,
            )

            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('menuadmin')
        except Exception as e:
            messages.error(request, f'Erro ao realizar o cadastro: {e}')

    # Passa 'usuarioLogado' para o template, garantindo que tenha valor
    return render(request, 'easy/cadastro_maquina.html', {'usuarioLogado': usuarioLogado})
# Na sua view de cadastro de funcionário:



def agenda(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipomanu = request.POST.get('tipomanu')
        dia = request.POST.get('dia')
        hora = request.POST.get('hora')
        quem = request.POST.get('quem')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO agendamento (nome, tipomanu, dia, hora, quem) VALUES (%s, %s, %s, %s, %s)",
                    [nome, tipomanu, dia, hora, quem]
                )
            messages.success(request, 'Agendamento salvo com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao salvar agendamento: {e}')

        return redirect('calendario')  # Redireciona para a página do calendário

    return render(request, 'easy/agenda.html')  # Renderiza o formulário de agendamento

def manual_maquinas(request):
    maquinas = Maquina.objects.all()  # Buscar todas as máquinas no banco de dados
    return render(request, 'easy/galeria_doc.html', {'maquinas': maquinas})

def capa(request):
    return render(request, 'easy/capa.html')

def menu(request):
    return render(request, 'easy/menu.html')

def menuadmin(request):
    return render(request, 'easy/menuadm.html')

def calendario(request):
    return render(request, 'easy/calendario.html')
