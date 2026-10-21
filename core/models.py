"""Contrato de dados do backend. Os fronts (terminal, GUI, voz) so consomem isto."""
from dataclasses import asdict, dataclass, field
from typing import Optional

VERSAO_CONTRATO = 1

NIVEIS = ("info", "aviso", "critico")


@dataclass
class Hora:
    saudacao: str
    periodo: str  # madrugada | manha | tarde | noite
    hora: str  # "22:04"
    data_extenso: str  # "terça-feira, 20 de outubro"
    iso: str


@dataclass
class Clima:
    cidade: str
    descricao: str
    temperatura: float
    sensacao: float
    minima: float
    maxima: float
    chuva_pct: int


@dataclass
class Tarefa:
    id: Optional[int]
    titulo: str
    prazo_iso: Optional[str]
    horas_restantes: Optional[float]
    prova: bool = False
    redacao: bool = False


@dataclass
class Tarefas:
    pendentes: int
    itens: list = field(default_factory=list)  # lista de Tarefa, ordenada por prazo
    atualizado_em: Optional[str] = None
    desatualizado: bool = False


@dataclass
class Alerta:
    id: str
    nivel: str  # info | aviso | critico
    texto: str
    origem: str  # sono | chuva | tarefa | ...


@dataclass
class Resultado:
    """Envelope de cada modulo: o front sempre sabe se deu certo e por que nao."""
    nome: str
    ok: bool
    dados: Optional[dict] = None
    erro: Optional[str] = None
    ms: int = 0


@dataclass
class Briefing:
    versao: int
    gerado_em: str
    usuario: str
    modulos: dict = field(default_factory=dict)  # nome -> Resultado
    alertas: list = field(default_factory=list)  # lista de Alerta

    def para_dict(self):
        return asdict(self)
