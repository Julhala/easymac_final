from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', capa, name='capa'),
    path('cadastro_funcionario/', cadastrar_usuario, name='cadastrar_usuario'),
    path('agenda/', agenda, name='agenda'),
    path('maquinas/', manual_maquinas, name='galeria_doc'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro_maquina/', cadastrar_maquina, name='cadastrar_maquina'),
    path('menu/', menu, name='menu'),
    path('menuadmin/', menuadmin, name='menuadmin'),
    path('logindoc/', login_view, name='loginfunc'),
    path('loginADMIN/', login_admin, name='loginADMIN'),
    path('calendario', calendario, name='calendario'),
    path("obter_eventos/", obter_eventos, name="obter_eventos"),
    path("obter_eventos/", obter_eventos, name="obter_eventos"),
    path("tabelasfuncionarios/", tabelas_view, name="tabela_funcionario"),
    path("tabelasmaquinas/", listar_maquinas, name="tabela_maquina"),
    path('editar_funcionario/<int:id>/', editar_funcionario, name='editar_funcionario'),
    path('excluir_funcionario/<int:id>/', excluir_funcionario, name='excluir_funcionario'),
    path('excluir_maquina/<int:id>/', excluir_maquina, name='excluir_maquina'),
    path('editar_maquina/<int:id>/', editar_maquina, name='editar_maquina'),
    path('funcionario/<int:id>/excluir/', excluir_funcionario, name='excluir_funcionario'),
    path('funcionarios/', lista_funcionarios, name='tabela_funcionario'),
    path('tabelasfuncionarios/', lista_funcionarios, name='tabela_funcionario'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
