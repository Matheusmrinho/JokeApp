#Importar o aplicativo, builder(GUI)
#Criar o app
#Criar a função build
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

import json
import requests
import random

Builder.load_file("tela2.kv")
link = "https://v2.jokeapi.dev/joke/Programming,Spooky"
last_joke = None
Mudo = False

class Gerenciador(ScreenManager):
    pass
class TelaSaida(Screen):
    def fecharapp(self):
        exit()
    
class Tela1(Screen):
    audio = None
    mudo = False
    audio_enabled = True  # Variável para controlar a reprodução do áudio

    def toggle_mudo(self):
        self.mudo = not self.mudo
        mudo_button = self.ids['mudo_button']
        if self.mudo:
            mudo_button.theme_text_color = 'Custom'
            mudo_button.text_color = [1, 0, 0, 1]  # Vermelhor quando mudo
            self.desativar_audio()
        else:
            mudo_button.theme_text_color = 'Custom'
            mudo_button.text_color = [0, 1, 0, 1]  # Verde quando não mudo
            self.ativar_audio()

    def desativar_audio(self):
        self.audio_enabled = False
        if self.audio:
            self.audio.stop()

    def ativar_audio(self):
        self.audio_enabled = True
        if not self.audio:
            self.audio = SoundLoader.load("risada.mp3")
    def abrir_selecao_linguagem(self):
        self.manager.current = 'selecao_linguagem'

    def abrir_telapiada(self):
        self.manager.current = 'selecao_linguagem'
        self.manager.current = 'telapiada'
        tela_piada = self.manager.get_screen('telapiada')
        piada, resposta = self.gerarpiada()
        tela_piada.carregar_dados(piada, resposta)
        while piada == self.last_piada:
            piada, resposta = self.gerarpiada()
        
        tela_piada.carregar_dados(piada, resposta)
        self.last_piada = piada  # Atualizar a última piada gerada

    def gerarpiada(self):
        global last_joke
        requisicao = requests.get(link)
        dic_requisicao = requisicao.json()

        if dic_requisicao['type'] == 'single':
            piada = dic_requisicao['joke']
            resposta = ''
        else:
            piada = dic_requisicao['setup']
            resposta = dic_requisicao['delivery']
        if piada == last_joke:
            return self.gerarpiada()  # Chamar a função novamente para gerar uma piada diferente

        last_joke = piada  # Atualizar a última piada gerada
        return piada, resposta
class TelaSelecaoLinguagem(Screen):
    def __init__(self, **kwargs):
        super(TelaSelecaoLinguagem, self).__init__(**kwargs)
        self.piadas_exibidas = []
    last_piada = None
    def abrir_telapiada(self, language):
        self.manager.current = 'telapiada'
        tela_piada = self.manager.get_screen('telapiada')
        if language == 'portugues':
            piada, resposta = self.gerarpiada_portugues()
        else:
            piada, resposta = self.gerarpiada()
        
        # Verificar se a piada gerada é diferente da última piada
        while piada == self.last_piada:
            if language == 'portugues':
                piada, resposta = self.gerarpiada_portugues()
            else:
                piada, resposta = self.gerarpiada()
        
        tela_piada.carregar_dados(piada, resposta)
        self.last_piada = piada  
    def gerarpiada(self):
        global last_joke
        requisicao = requests.get(link)
        dic_requisicao = requisicao.json()

        if dic_requisicao['type'] == 'single':
            piada = dic_requisicao['joke']
            resposta = ''
        else:
            piada = dic_requisicao['setup']
            resposta = dic_requisicao['delivery']
        if piada == last_joke:
            return self.gerarpiada()  # Chamar a função novamente para gerar uma piada diferente

        last_joke = piada  # Atualizar a última piada gerada
        return piada, resposta
    def on_lang_select(self, lang):
        if lang == 'portugues':
            self.exibir_piada_portugues()
    def exibir_piada_portugues(self):
        setup, resposta = self.gerarpiada_portugues()
        tela_piada = self.manager.get_screen('telapiada')
        tela_piada.carregar_dados(setup, resposta)
    def gerarpiada_portugues(self):
        with open("piadas.json", "r", encoding="utf-8") as file:
            piadas = json.load(file)

        # Filtrar piadas que ainda não foram exibidas
        piadas_nao_exibidas = [piada for piada in piadas if piada['id'] not in self.piadas_exibidas]

        if not piadas_nao_exibidas:
            # Todas as piadas foram exibidas, reinicializar a lista de piadas exibidas
            self.piadas_exibidas = []

        piada_escolhida = random.choice(piadas_nao_exibidas)
        self.piadas_exibidas.append(piada_escolhida['id'])

        tipo = piada_escolhida.get("type", "")

        if tipo == "twopart":
            setup = piada_escolhida.get("setup", "")
            resposta = piada_escolhida.get("delivery", "")
        elif tipo == "single":
            setup = piada_escolhida.get("joke", "")
            resposta = ""
        else:
            setup = "Piada indisponível"
            resposta = ""

        return setup, resposta
class TelaPiada(Screen):
    mudo = False
    audio = None

    def toggle_mudo(self):
        self.mudo = not self.mudo
        mudo_button = self.ids['mudo_button']
        if self.mudo:
            mudo_button.theme_text_color = 'Custom'
            mudo_button.text_color = [0, 1, 0, 1]  # Verde quando mudo
            self.desativar_audio()
        else:
            mudo_button.theme_text_color = 'Custom'
            mudo_button.text_color = [1, 0, 0, 1]  # Vermelho quando não mudo
            self.ativar_audio()

    def desativar_audio(self):
        if self.audio:
            self.audio.stop()

    def ativar_audio(self):
        if not self.audio:
            self.audio = SoundLoader.load("risada.mp3")

    audio = None

    def on_enter(self):
        tela1 = self.manager.get_screen('home')  # Acessar a tela Tela1
        if tela1.audio_enabled:
            self.audio = SoundLoader.load("risada.mp3")
            if self.audio:
                self.audio.play()
                Clock.schedule_once(self.stop_audio, 10) 
    def on_leave(self):
        Clock.schedule_once(self.stop_audio, 1)  # Agendando o encerramento após 1 segundo

    def stop_audio(self, dt):
        if self.audio:
            self.audio.stop()

    def carregar_dados(self, piada, resposta):
        self.ids['setup'].text = piada
        self.ids['resposta'].text = "\n\n" + resposta  # Adiciona uma quebra de linha antes da resposta
        
class Jokes(MDApp):
    def build(self):
        self.icon = "icone.png"
        self.theme_cls.primary_palette = "Teal"
        self.screen_manager = ScreenManager()
        self.home_screen = Tela1(name="home")
        self.telapiada_screen = TelaPiada(name='telapiada')
        self.selecaolinguagem_screen = TelaSelecaoLinguagem(name='selecao_linguagem')
        self.telasaida_screen = TelaSaida(name= 'telasaida')
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.telapiada_screen)
        self.screen_manager.add_widget(self.selecaolinguagem_screen)
        self.screen_manager.add_widget(self.telasaida_screen)
        return self.screen_manager

    def on_start(self):
        Builder.load_file("tela2.kv")

    def gerarpiada(self):
        requisicao = requests.get(link)
        dic_requisicao = requisicao.json()

        if dic_requisicao['type'] == 'single':
            piada = dic_requisicao['joke']
            resposta = ''
        else:
            piada = dic_requisicao['setup']
            resposta = dic_requisicao['delivery']

        return piada, resposta

    def on_lang_select(self, lang):
        self.root.get_screen('selecao_linguagem').on_lang_select(lang)

Jokes().run()