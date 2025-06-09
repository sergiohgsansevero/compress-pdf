import fitz
import os
from PIL import Image
import io

PASTA_PDFS = '.'
SAIDA_PASTA = './comprimidos'
TAMANHO_ALVO_KB = 200
INTERVALO_TOLERANCIA = 20  # +/- 20 KB

os.makedirs(SAIDA_PASTA, exist_ok=True)

def comprimir_ate_tamanho_alvo(caminho_pdf, caminho_saida, tamanho_alvo_kb=TAMANHO_ALVO_KB):
    qualidade = 20
    zoom = 0.5
    max_qualidade = 90
    max_zoom = 1.5
    passo_qualidade = 10
    passo_zoom = 0.1

    while True:
        doc = fitz.open(caminho_pdf)
        nova_doc = fitz.open()

        for pagina in doc:
            mat = fitz.Matrix(zoom, zoom)
            pix = pagina.get_pixmap(matrix=mat, alpha=False)
            img_bytes = pix.tobytes(output="png")

            img = Image.open(io.BytesIO(img_bytes))
            img_byte_arr = io.BytesIO()
            img = img.convert("RGB")
            img.save(img_byte_arr, format='JPEG', quality=qualidade)
            img_byte_arr = img_byte_arr.getvalue()

            nova_pagina = nova_doc.new_page(width=img.width, height=img.height)
            nova_pagina.insert_image(nova_pagina.rect, stream=img_byte_arr)

        nova_doc.save(caminho_saida)
        nova_doc.close()
        doc.close()

        tamanho_atual_kb = os.path.getsize(caminho_saida) / 1024

        # print pra debug
        print(f"Tamanho: {int(tamanho_atual_kb)} KB | Qualidade: {qualidade} | Zoom: {zoom:.2f}")

        # Checa se está dentro da faixa aceitável
        if tamanho_alvo_kb - INTERVALO_TOLERANCIA <= tamanho_atual_kb <= tamanho_alvo_kb + INTERVALO_TOLERANCIA:
            break

        # Se ficou menor que a faixa, aumenta qualidade/zoom
        if tamanho_atual_kb < tamanho_alvo_kb - INTERVALO_TOLERANCIA:
            if qualidade + passo_qualidade <= max_qualidade:
                qualidade += passo_qualidade
            elif zoom + passo_zoom <= max_zoom:
                qualidade = 20  # resetar qualidade para aumentar zoom
                zoom += passo_zoom
            else:
                # Já no máximo, para
                break
        else:
            # Se ficou maior que o alvo, diminui qualidade/zoom
            if qualidade - passo_qualidade >= 20:
                qualidade -= passo_qualidade
            elif zoom - passo_zoom >= 0.5:
                qualidade = max_qualidade  # reset qualidade para máximo e diminuir zoom
                zoom -= passo_zoom
            else:
                break

def processar_pdfs():
    arquivos_pdf = [f for f in os.listdir(PASTA_PDFS) if f.lower().endswith('.pdf') and os.path.isfile(f)]

    if not arquivos_pdf:
        print("Nenhum PDF encontrado.")
        return

    for arquivo in arquivos_pdf:
        caminho_original = os.path.join(PASTA_PDFS, arquivo)
        caminho_saida = os.path.join(SAIDA_PASTA, arquivo)

        print(f"Processando {arquivo}...")
        comprimir_ate_tamanho_alvo(caminho_original, caminho_saida)

        tamanho_kb = os.path.getsize(caminho_saida) / 1024
        print(f"Final: {arquivo} com {int(tamanho_kb)} KB\n")

if __name__ == '__main__':
    processar_pdfs()
