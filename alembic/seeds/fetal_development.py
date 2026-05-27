"""
Seed: fetal_development
Run: python alembic/seeds/fetal_development.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.database import AsyncSessionLocal
from app.models.fetal_development import FetalDevelopment

# (week, size_cm, weight_g, description, highlights)
WEEKS = [
    (1, None, None,
     "A jornada começa! O óvulo é fertilizado pelo espermatozoide, formando uma célula única chamada zigoto com todo o material genético do bebê.",
     [{"id": "1", "label": "Fertilização", "description": "Encontro do óvulo com o espermatozoide."},
      {"id": "2", "label": "DNA completo", "description": "Todo o código genético do bebê já está definido."}]),

    (2, None, None,
     "O zigoto se divide rapidamente enquanto viaja pela tuba uterina em direção ao útero. No final da semana, uma blástula se implanta no endométrio.",
     [{"id": "1", "label": "Divisão celular", "description": "O zigoto vira mórula, depois blástula."},
      {"id": "2", "label": "Implantação", "description": "Fixação no endométrio uterino."}]),

    (3, 0.1, None,
     "O embrião tem menos de 1 mm. As camadas germinativas (ectoderma, mesoderma e endoderma) começam a se formar, dando origem a todos os órgãos.",
     [{"id": "1", "label": "Camadas germinativas", "description": "Estruturas que originarão todos os órgãos."},
      {"id": "2", "label": "Gastrulação", "description": "Reorganização celular fundamental."}]),

    (4, 0.4, None,
     "O tubo neural — que se tornará o cérebro e a medula espinhal — começa a se fechar. O coração primitivo já bate esporadicamente.",
     [{"id": "1", "label": "Tubo neural", "description": "Futuro sistema nervoso central."},
      {"id": "2", "label": "Primeiro batimento", "description": "Coração primitivo inicia atividade elétrica."}]),

    (5, 0.5, None,
     "O coração bate de forma rítmica. Brotos dos membros superiores começam a aparecer. Seu tamanho é o de um grão de arroz.",
     [{"id": "1", "label": "Coração rítmico", "description": "Cerca de 100 batimentos por minuto."},
      {"id": "2", "label": "Brotos dos braços", "description": "Primórdios dos membros superiores."}]),

    (6, 0.6, None,
     "O embrião tem formato de 'C'. Brotos dos membros inferiores surgem. O cérebro se divide em suas três regiões principais.",
     [{"id": "1", "label": "Brotos das pernas", "description": "Primórdios dos membros inferiores."},
      {"id": "2", "label": "Divisão cerebral", "description": "Prosencéfalo, mesencéfalo e rombencéfalo."}]),

    (7, 1.0, None,
     "Braços e pernas se alongam. Os dedos das mãos começam a se diferenciar. O rosto ganha contornos: olhos, narinas e boca primitivos.",
     [{"id": "1", "label": "Diferenciação digital", "description": "Dedos começam a se formar."},
      {"id": "2", "label": "Traços faciais", "description": "Olhos, nariz e boca primitivos visíveis."}]),

    (8, 1.6, 1.0,
     "A cauda embrionária desaparece. Todos os órgãos principais estão presentes em forma primitiva. Movimentos espontâneos começam.",
     [{"id": "1", "label": "Fim da cauda", "description": "O embrião adquire forma humana reconhecível."},
      {"id": "2", "label": "Órgãos formados", "description": "Coração, pulmões, fígado e rins presentes."}]),

    (9, 2.3, 2.0,
     "O embrião é agora oficialmente um feto. Os dedos estão separados. As pálpebras estão fechadas e protegem os olhos em desenvolvimento.",
     [{"id": "1", "label": "Fase fetal", "description": "Início do período fetal, menor risco de malformações."},
      {"id": "2", "label": "Dedos separados", "description": "Mãos e pés com dedos individuais."}]),

    (10, 3.1, 4.0,
     "O bebê pode dobrar os joelhos e chutar. Os dentes de leite começam a se formar nas gengivas. O fígado produz sangue.",
     [{"id": "1", "label": "Movimentos de chute", "description": "Pernas se movem, mas ainda não são sentidas."},
      {"id": "2", "label": "Dentes de leite", "description": "Brotos dentários se formam nas gengivas."}]),

    (11, 4.1, 7.0,
     "O rosto está mais humano. Os ossos começam a endurecer. O bebê é capaz de abrir e fechar as mãos.",
     [{"id": "1", "label": "Ossificação", "description": "Cartilagens começam a se transformar em osso."},
      {"id": "2", "label": "Preensão", "description": "Mãos abrem e fecham reflexamente."}]),

    (12, 5.4, 14.0,
     "Fim do primeiro trimestre! Todos os órgãos estão formados. O risco de aborto diminui significativamente. O bebê tem unhas.",
     [{"id": "1", "label": "Fim do 1º trimestre", "description": "Marco importante na gestação."},
      {"id": "2", "label": "Unhas formadas", "description": "Unhas finas aparecem nos dedos."},
      {"id": "3", "label": "Órgãos completos", "description": "Todos os órgãos presentes e em desenvolvimento."}]),

    (13, 7.4, 23.0,
     "Segundo trimestre começa! Os reflexos melhoram. O intestino começa a se mover para dentro do abdômen. As impressões digitais se formam.",
     [{"id": "1", "label": "Impressões digitais", "description": "Marcas únicas se formam nos dedos."},
      {"id": "2", "label": "Intestino migra", "description": "Intestino retorna do cordão para o abdômen."}]),

    (14, 8.7, 43.0,
     "O bebê pode chupar o polegar. O sexo pode ser identificado por ultrassom. A glândula tireoide começa a funcionar.",
     [{"id": "1", "label": "Polegar na boca", "description": "Reflexo de sucção já presente."},
      {"id": "2", "label": "Identificação do sexo", "description": "Órgãos genitais distinguíveis por ultrassom."}]),

    (15, 10.1, 70.0,
     "O bebê pode ouvir sons. Os ossos estão ficando mais fortes. Lanugo — pelos finos — cobre o corpo para manter a temperatura.",
     [{"id": "1", "label": "Audição", "description": "Ouvidos funcionais, bebê ouve a voz da mãe."},
      {"id": "2", "label": "Lanugo", "description": "Pelos finos que regulam a temperatura corporal."}]),

    (16, 11.6, 100.0,
     "A mãe pode começar a sentir os primeiros movimentos (fluttuazione). Os olhos se movem sob as pálpebras fechadas.",
     [{"id": "1", "label": "Primeiros movimentos", "description": "Sensação de borboletas no abdômen."},
      {"id": "2", "label": "Movimentos oculares", "description": "Olhos se movem, mesmo fechados."}]),

    (17, 13.0, 140.0,
     "O tecido adiposo começa a se acumular. O bebê desenvolve reflexos de engolir e piscar. O cordão umbilical fica mais espesso.",
     [{"id": "1", "label": "Gordura corporal", "description": "Camada de gordura começa a se formar."},
      {"id": "2", "label": "Reflexo de engolir", "description": "Bebê engole líquido amniótico regularmente."}]),

    (18, 14.2, 190.0,
     "O sistema nervoso avança rapidamente. O bebê tem períodos de sono e vigília. Impressionante: já tem papilas gustativas!",
     [{"id": "1", "label": "Papilas gustativas", "description": "Bebê já sente sabores no líquido amniótico."},
      {"id": "2", "label": "Ciclo sono-vigília", "description": "Bebê dorme e acorda como recém-nascido."}]),

    (19, 15.3, 240.0,
     "O vérnix caseoso — substância branca e protetora — cobre a pele. As mães que já tiveram filhos podem sentir os movimentos claramente.",
     [{"id": "1", "label": "Vérnix caseoso", "description": "Revestimento gorduroso que protege a pele no líquido."},
      {"id": "2", "label": "Movimentos sentidos", "description": "Chutes e rolamentos mais perceptíveis."}]),

    (20, 16.4, 300.0,
     "Metade da gestação! O bebê pesa cerca de 300g. Por ultrassom morfológico, todos os órgãos são avaliados detalhadamente.",
     [{"id": "1", "label": "Marco da metade", "description": "20 semanas: ponto central da gestação."},
      {"id": "2", "label": "Ultrassom morfológico", "description": "Avaliação completa dos órgãos e estruturas."},
      {"id": "3", "label": "Sobrancelhas e cílios", "description": "Sobrancelhas e cílios já estão presentes."}]),

    (21, 26.7, 360.0,
     "O bebê se move muito e pode reagir a sons externos. As sobrancelhas e cílios estão formados. Unhas crescem até a ponta dos dedos.",
     [{"id": "1", "label": "Reação a sons", "description": "Bebê se move ao ouvir músicas ou voz alta."},
      {"id": "2", "label": "Unhas completas", "description": "Unhas chegam à ponta dos dedos."}]),

    (22, 27.8, 430.0,
     "Os pulmões se preparam para respirar: produzem surfactante. O bebê pode sentir dor. Lábios e pálpebras bem definidos.",
     [{"id": "1", "label": "Surfactante", "description": "Substância que evitará o colapso pulmonar ao nascer."},
      {"id": "2", "label": "Sensação de dor", "description": "Sistema nervoso capaz de processar dor."}]),

    (23, 28.9, 501.0,
     "Limite de viabilidade! Bebês nascidos a partir de 23 semanas podem sobreviver com suporte intensivo. O cérebro cresce rapidamente.",
     [{"id": "1", "label": "Viabilidade", "description": "Sobrevivência com UTI neonatal especializada."},
      {"id": "2", "label": "Crescimento cerebral", "description": "Cérebro forma sulcos e giros."}]),

    (24, 30.0, 600.0,
     "Os pulmões continuam amadurecendo. O bebê pode piscar. Com ultrassom, é possível ver os traços do rosto com clareza.",
     [{"id": "1", "label": "Piscar", "description": "Reflexo de piscar desenvolvido."},
      {"id": "2", "label": "Feições visíveis", "description": "Rosto detalhado visível por ultrassom 4D."}]),

    (25, 34.6, 660.0,
     "A gordura subcutânea aumenta, dando ao bebê aparência mais arredondada. A pele fica menos translúcida. Cabelos já visíveis.",
     [{"id": "1", "label": "Gordura subcutânea", "description": "Bebê fica mais rechonchudo."},
      {"id": "2", "label": "Cabelo visível", "description": "Cabelo começa a aparecer no couro cabeludo."}]),

    (26, 35.6, 760.0,
     "Os olhos se abrem pela primeira vez! O bebê responde à luz. O sistema imunológico começa a se desenvolver com ajuda materna.",
     [{"id": "1", "label": "Olhos abertos", "description": "Pálpebras se abrem e fecham."},
      {"id": "2", "label": "Resposta à luz", "description": "Bebê reage a lanterna sobre o abdômen."}]),

    (27, 36.6, 875.0,
     "Final do segundo trimestre. O cérebro está mais ativo. O bebê pode reconhecer a voz dos pais. A maioria está de cabeça para baixo.",
     [{"id": "1", "label": "Reconhecimento vocal", "description": "Bebê prefere a voz da mãe a outros sons."},
      {"id": "2", "label": "Posição cefálica", "description": "Maioria começa a se posicionar para o parto."}]),

    (28, 37.6, 1005.0,
     "Terceiro trimestre! O bebê pesa cerca de 1 kg. Os pulmões estão mais maduros. Sonhos são possíveis — o sono REM está presente.",
     [{"id": "1", "label": "1 quilo!", "description": "Marco de peso importante na gestação."},
      {"id": "2", "label": "Sono REM", "description": "Bebê pode ter atividade de sonho."},
      {"id": "3", "label": "Início do 3º trimestre", "description": "Fase final e de crescimento acelerado."}]),

    (29, 38.6, 1153.0,
     "Os ossos estão quase totalmente formados. O bebê pratica movimentos respiratórios. A cabeça cresce para acomodar o cérebro em desenvolvimento.",
     [{"id": "1", "label": "Movimentos respiratórios", "description": "Pratica respiração com líquido amniótico."},
      {"id": "2", "label": "Ossificação avançada", "description": "Esqueleto quase completo."}]),

    (30, 39.9, 1319.0,
     "O lanugo começa a desaparecer. O bebê pode ver luz e sombra. Unhas crescem rápido. O espaço no útero diminui.",
     [{"id": "1", "label": "Lanugo desaparece", "description": "Pelos finos somem à medida que há mais gordura."},
      {"id": "2", "label": "Visão de luz", "description": "Percebe claridade através da parede abdominal."}]),

    (31, 41.1, 1502.0,
     "O bebê vai de olhos abertos durante a vigília e fechados durante o sono. Pode virar a cabeça de lado a lado. Unhas chegam à ponta dos dedos.",
     [{"id": "1", "label": "Ciclo olhos abertos/fechados", "description": "Vigília e sono bem definidos."},
      {"id": "2", "label": "Movimentos da cabeça", "description": "Gira a cabeça de forma coordenada."}]),

    (32, 42.4, 1702.0,
     "Os órgãos sexuais externos estão completamente formados. O bebê engole cerca de 1 litro de líquido amniótico por dia.",
     [{"id": "1", "label": "Órgãos sexuais completos", "description": "Genitália externa totalmente desenvolvida."},
      {"id": "2", "label": "Deglutição ativa", "description": "1 litro de líquido amniótico por dia."}]),

    (33, 43.7, 1918.0,
     "Os pulmões estão quase maduros. O crânio está mole e flexível para facilitar o parto. O bebê acumula gordura rapidamente.",
     [{"id": "1", "label": "Crânio flexível", "description": "Ossos do crânio sobrepostos facilitam o parto."},
      {"id": "2", "label": "Pulmões maduros", "description": "Produção de surfactante em bom nível."}]),

    (34, 45.0, 2146.0,
     "O vérnix caseoso cobre o bebê em abundância. As unhas dos pés chegam às pontas. Sistema nervoso central bastante desenvolvido.",
     [{"id": "1", "label": "Vérnix abundante", "description": "Proteção máxima da pele no útero."},
      {"id": "2", "label": "Unhas dos pés", "description": "Chegam à ponta dos artelhos."}]),

    (35, 46.2, 2383.0,
     "Os rins estão completamente formados. O fígado processa resíduos. O bebê prefere posição fetal. Quase 2,5 kg.",
     [{"id": "1", "label": "Rins completos", "description": "Filtram o sangue e produzem urina ativamente."},
      {"id": "2", "label": "Fígado funcional", "description": "Armazena ferro e glicose."}]),

    (36, 47.4, 2622.0,
     "Bebê considerado quase a termo. As bochechas estão cheias de gordura para auxiliar na sucção. A maioria está de cabeça para baixo.",
     [{"id": "1", "label": "Quase a termo", "description": "36 semanas: alta chance de sobrevida sem suporte."},
      {"id": "2", "label": "Bochechas gordas", "description": "Preparo muscular para amamentação."}]),

    (37, 48.6, 2859.0,
     "Bebê a termo precoce! O sistema imunológico recebe anticorpos da mãe. Os pulmões estão prontos para respirar ar.",
     [{"id": "1", "label": "A termo precoce", "description": "37 semanas: clinicamente a termo."},
      {"id": "2", "label": "Anticorpos maternos", "description": "Imunidade passada pela placenta."},
      {"id": "3", "label": "Pulmões prontos", "description": "Surfactante suficiente para respiração ar."}]),

    (38, 49.8, 3083.0,
     "O vérnix começa a desaparecer. O bebê está totalmente pronto. Pode nascer a qualquer momento. Movimentos podem diminuir por falta de espaço.",
     [{"id": "1", "label": "Vérnix diminui", "description": "Pele fica mais lisa conforme se aproxima o parto."},
      {"id": "2", "label": "Totalmente pronto", "description": "Todos os sistemas funcionando."}]),

    (39, 50.7, 3288.0,
     "O bebê acumula gordura até o último momento. O cérebro continua crescendo. O cordão umbilical tem cerca de 50 cm.",
     [{"id": "1", "label": "Gordura final", "description": "Reservas de energia para as primeiras horas de vida."},
      {"id": "2", "label": "Cordão umbilical", "description": "Mede em média 50 cm de comprimento."}]),

    (40, 51.2, 3462.0,
     "A data provável do parto chegou! O bebê está completamente desenvolvido. A placenta começa a envelhecer. Qualquer semana o bebê pode nascer.",
     [{"id": "1", "label": "Data provável do parto", "description": "DPP — bebê completamente desenvolvido."},
      {"id": "2", "label": "Placenta envelhecendo", "description": "Sinal de que o bebê está pronto para sair."},
      {"id": "3", "label": "Peso médio", "description": "Cerca de 3,4 kg e 51 cm."}]),

    (41, 51.7, 3597.0,
     "Pós-data. Médico monitorará a frequência cardíaca fetal e o líquido amniótico. A indução pode ser recomendada.",
     [{"id": "1", "label": "Monitoramento intensivo", "description": "CTG e ultrassom frequentes."},
      {"id": "2", "label": "Indução possível", "description": "Pode ser recomendada com 41 semanas."}]),

    (42, 52.0, 3685.0,
     "Pós-maturidade. Bebê pode ter pele seca e descamada, unhas longas e lanugo ausente. A indução do trabalho de parto é geralmente indicada.",
     [{"id": "1", "label": "Pós-maduro", "description": "Bebê com características de pós-maturidade."},
      {"id": "2", "label": "Indicação de indução", "description": "Protocolo padrão após 42 semanas completas."}]),
]


async def run():
    async with AsyncSessionLocal() as db:
        import sqlalchemy as sa
        existing = (
            await db.execute(sa.select(sa.func.count()).select_from(FetalDevelopment))
        ).scalar_one()
        if existing > 0:
            print(f"Skipping: {existing} weeks already seeded.")
            return

        records = [
            FetalDevelopment(
                week=week,
                size_cm=size_cm,
                weight_g=weight_g,
                description=description,
                highlights=highlights,
            )
            for week, size_cm, weight_g, description, highlights in WEEKS
        ]
        db.add_all(records)
        await db.commit()
        print(f"Seeded {len(records)} weeks of fetal development data.")


if __name__ == "__main__":
    asyncio.run(run())
