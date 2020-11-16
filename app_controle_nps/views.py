from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app_controle_nps.models import Pesquisa, Questao
from app_controle_nps.serializers import UsuarioSerializer, PesquisaSerializer, RealizarPesquisaSerializer
from rest_framework.authtoken.models import Token

from util.choicesModels import PESQUISADOR, INICIADA, CRIADA, FINALIZADA
from django.shortcuts import get_object_or_404


class IsAutenticatedListApiView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([TokenAuthentication])


'''
Classe responsável por validar o Pesquisador autenticado, caso tente usar um Token de um outro tipo de usuário,
o sistema retornar o erro Usuário sem permissão
'''


class PesquisadorAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token = get_object_or_404(Token, pk=key)

        if token.user.usuario.tipo != PESQUISADOR:
            responser = dict(detail="Usuário sem permissão.")
            raise exceptions.AuthenticationFailed(responser)
        return super().authenticate_credentials(key)


'''
LoginView - retornar os dados do usuario logado - Token principalmente.
Caso o token não exista o acesso irá criá-lo

'''


class LoginView(GenericAPIView):
    serializer_class = UsuarioSerializer

    def post(self, request):
        user = authenticate(username=request.data['email'], password=request.data['senha'])
        if user is None:
            return Response({"detail": "Usuário ou senha inválido"}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response(user.usuario.get_json(), status=status.HTTP_200_OK)


'''
- Lista de pesquisas: disponível para todos os usuários autenticados, pesquisadores (todas as
pesquisas disponíveis) e pesquisados (apenas as pesquisas iniciadas e ainda não respondidas)
'''


class PesquisaListView(IsAutenticatedListApiView):
    queryset = Pesquisa.objects.none()
    serializer_class = PesquisaSerializer

    def get_queryset(self):
        usuario = self.request.user.usuario
        # pesquisadores (todas as pesquisas disponíveis)
        if usuario.tipo == PESQUISADOR:
            query = Pesquisa.objects.all()
        else:
            # pesquisados (apenas as pesquisas iniciadas e ainda não respondidas)
            query = Pesquisa.objects.filter(status=INICIADA)
        return query


'''
- Detalhe de pesquisa: disponível para todos os usuários autenticados, pesquisadores ( todas
as pesquisas disponíveis e com detalhes NPS de pesquisas finalizadas) e pesquisados (apenas
as pesquisas iniciadas e ainda não respondidas)
'''


class PesquisaDetalhe(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([TokenAuthentication])

    def get(self, request, pk):
        print('get')
        # pesquisa = Pesquisa.objects.get(pk=pk)
        pesquisa = get_object_or_404(Pesquisa, pk=pk)

        # pesquisadores ( todas as pesquisas disponíveis e com detalhes NPS de pesquisas finalizadas)
        if self.request.user.usuario.tipo == PESQUISADOR:
            dados = pesquisa.get_json_detalheNPS()
        else:
            # pesquisados (apenas as pesquisas iniciadas e ainda não respondidas)
            dados = pesquisa.get_json()

        return Response(dados, status=status.HTTP_200_OK)


'''
- iniciar pesquisa: disponível apenas para pesquisadores autenticados

Como não ficou claro que teria que enviar dados da pesquisa, só estou mudando o status para INICIADA, caso
anteriormente o status fosse CRIADA
'''


class IniciarPesquisa(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request, pk):
        print('get')
        # pesquisa = Pesquisa.objects.get(pk=pk)
        pesquisa = get_object_or_404(Pesquisa, pk=pk)

        if pesquisa.status == INICIADA:
            return Response({'detail': "Pesquisa já foi Iniciada em {}".format(pesquisa.data_cadastro)},
                            status=status.HTTP_401_UNAUTHORIZED)
        if pesquisa.status == FINALIZADA:
            return Response({'detail': "Pesquisa já finalizada".format(pesquisa.data_cadastro)},
                            status=status.HTTP_401_UNAUTHORIZED)

        pesquisa.status = INICIADA
        pesquisa.save()
        return Response({'detail': "Pesquisa Iniciada"}, status=status.HTTP_200_OK)


'''
- Finalizar pesquisa: disponível apenas para pesquisadores autenticados
'''


class FinalizarPesquisa(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request, pk):
        print('get')
        # pesquisa = Pesquisa.objects.get(pk=pk)
        pesquisa = get_object_or_404(Pesquisa, pk=pk)

        if pesquisa.status == FINALIZADA:
            return Response({'detail': "Pesquisa já finalizada em {}".format(pesquisa.date_modificado)},
                            status=status.HTTP_401_UNAUTHORIZED)
        if pesquisa.status == CRIADA:
            return Response({'detail': "Essa Pesquisa ainda não foi Iniada".format(pesquisa.data_cadastro)},
                            status=status.HTTP_401_UNAUTHORIZED)

        pesquisa.status = FINALIZADA
        pesquisa.save()
        return Response({'detail': "Pesquisa Finalizada com Sucesso"}, status=status.HTTP_200_OK)


class RespostasPesquisaListView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = ([PesquisadorAuthentication])

    def get(self, request):
        dados = []

        pesquisas = Pesquisa.objects.filter(status=FINALIZADA)

        for pesquisa in pesquisas:
            questoes = pesquisa.questoes_pesquisas.all()
            questoes = [questao.get_json_respostas() for questao in questoes]
            pesquisa = {
                'id': pesquisa.id,
                'descricao': pesquisa.descricao,
                'status': pesquisa.status,
                'questoes': questoes
            }
            dados.append(pesquisa)

        return JsonResponse(dados, status=status.HTTP_200_OK, safe=False)
