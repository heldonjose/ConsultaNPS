from django.urls import path, include
from app_controle_nps.views import LoginView, PesquisaListView, IniciarPesquisa, FinalizarPesquisa, \
    ListaRespostasPesquisaFinalizadaListView, PesquisaDetalhe, RealizarPesquisa

urlpatterns = [
    path("login_usuario/", LoginView.as_view(), name="login_usuario"),
    path("pesquisas/", PesquisaListView.as_view(), name="pesquisa_list_view"),
    path("pesquisa_detalhe/<int:pk>", PesquisaDetalhe.as_view(), name="pesquisa_detalhe"),
    path("finalizar_pesquisa/<int:pk>", FinalizarPesquisa.as_view(), name="finalizar_pesquisa"),
    path("realizar_pesquisa/<int:pk>", RealizarPesquisa.as_view(), name="realizar_pesquisa"),


    path("iniciar_pesquisa/<int:pk>", IniciarPesquisa.as_view(), name="iniciar_pesquisa"),
    path("respostas_pesquisas_finalizadas", ListaRespostasPesquisaFinalizadaListView.as_view(), name="respostas_pesquisas_finalizadas")
    ]