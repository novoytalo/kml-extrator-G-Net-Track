import os
import csv
import re
from lxml import etree
from tkinter import Tk
from tkinter.filedialog import askdirectory


def extrair_dados_kml(caminho_arquivo):
    try:
        dados = []

        with open(caminho_arquivo, 'rb') as arquivo:
            arvore = etree.parse(arquivo)
            root = arvore.getroot()

            nsmap = root.nsmap
            if None in nsmap:
                # Trata o namespace vazio, se existir
                nsmap['ns'] = nsmap.pop(None)

            placemarks = root.xpath('//ns:Placemark', namespaces=nsmap)

            for placemark in placemarks:
                point = placemark.xpath('.//ns:Point', namespaces=nsmap)[0]
                coordinates = point.xpath(
                    './/ns:coordinates', namespaces=nsmap)[0].text
                longitude, latitude, _ = coordinates.split(',')

                extended_data = placemark.xpath(
                    './/ns:ExtendedData', namespaces=nsmap)[0]
                cgi = extended_data.xpath(
                    './/ns:Data[@name="CGI"]/ns:value', namespaces=nsmap)
                cgi_value = cgi[0].text if cgi else ""

                # node = extended_data.xpath(
                #    './/ns:Data[@name="RNC"]/ns:value', namespaces=nsmap)
                # node_value = node[0].text if node else ""
                node = extended_data.xpath(
                    './/ns:Data[@name="eNB"]/ns:value', namespaces=nsmap)
                node_value = node[0].text if node else ""

                cellid = extended_data.xpath(
                    './/ns:Data[@name="CELLID"]/ns:value', namespaces=nsmap)
                cellid_value = cellid[0].text if cellid else ""

                pc = extended_data.xpath(
                    './/ns:Data[@name="PC"]/ns:value', namespaces=nsmap)
                pc_value = pc[0].text if pc else ""

                technology = extended_data.xpath(
                    './/ns:Data[@name="TECHNOLOGY"]/ns:value', namespaces=nsmap)
                technology_value = technology[0].text if technology else ""

                rsrp = extended_data.xpath(
                    './/ns:Data[@name="RSRP"]/ns:value', namespaces=nsmap)
                rsrp_value = rsrp[0].text if rsrp else ""

                rsrq = extended_data.xpath(
                    './/ns:Data[@name="RSRQ"]/ns:value', namespaces=nsmap)
                rsrq_value = rsrq[0].text if rsrq else ""

                dl_bitrate = extended_data.xpath(
                    './/ns:Data[@name="DL_BITRATE"]/ns:value', namespaces=nsmap)
                dl_bitrate_value = dl_bitrate[0].text if dl_bitrate else ""

                ul_bitrate = extended_data.xpath(
                    './/ns:Data[@name="UL_BITRATE"]/ns:value', namespaces=nsmap)
                ul_bitrate_value = ul_bitrate[0].text if ul_bitrate else ""

                snr = extended_data.xpath(
                    './/ns:Data[@name="SNR"]/ns:value', namespaces=nsmap)
                snr_value = snr[0].text if snr else ""

                # color = extended_data.xpath(
                #    './/ns:Data[@name="color"]/ns:value', namespaces=nsmap)
                # color_value = color[0].text if color else ""

                time = extended_data.xpath(
                    './/ns:Data[@name="TIME"]/ns:value', namespaces=nsmap)
                time_value = time[0].text if time else ""

                band = extended_data.xpath(
                    './/ns:Data[@name="BAND"]/ns:value', namespaces=nsmap)
                band_value = band[0].text if band else ""

                band_with = extended_data.xpath(
                    './/ns:Data[@name="BANDWIDTH"]/ns:value', namespaces=nsmap)
                band_with_value = band_with[0].text if band_with else ""

                height = extended_data.xpath(
                    './/ns:Data[@name="HEIGHT"]/ns:value', namespaces=nsmap)
                height_value = height[0].text if height else ""

                numeric_part = re.search(r"-?\d+", rsrp_value).group()
                rsrp_numeric = int(numeric_part)
                rsrq_part = re.search(r"-?\d+", rsrq_value).group()
                rsrq_numeric = int(rsrq_part)
                # if technology_value == "5G" and rsrp_numeric < 0 and rsrq_numeric < 0:
                # len band_with_value make sure that it only 10 or 20 or 30.
                if technology_value == "4G" and rsrp_numeric < 0 and rsrq_numeric < 0 and len(band_with_value) < 3:
                    # technology_value = "LTE"
                    dados.append([latitude, longitude, cgi_value, node_value, cellid_value, pc_value, technology_value,
                                  rsrp_numeric, rsrq_numeric, dl_bitrate_value, ul_bitrate_value, snr_value, time_value, band_value, band_with_value, height_value])

        return dados

    except etree.XMLSyntaxError as e:
        print(f"Erro ao analisar o arquivo: {caminho_arquivo}")
        print(f"Mensagem de erro: {e}")

    except Exception as e:
        print(f"Erro inesperado ao processar o arquivo: {caminho_arquivo}")
        print(f"Mensagem de erro: {e}")

    return []


def percorrer_pasta():
    # Abrir o diálogo para seleção da pasta raiz
    root = Tk()
    root.withdraw()
    pasta_raiz = askdirectory(
        title="Selecione a pasta raiz para busca dos arquivos KML")

    # Verificar se a seleção de pasta foi cancelada
    if not pasta_raiz:
        print("Seleção de pasta raiz cancelada.")
        return

    # Abrir o diálogo para seleção da pasta de destino
    pasta_destino = askdirectory(
        title="Selecione a pasta de destino para os arquivos tratados")

    # Verificar se a seleção de pasta foi cancelada
    if not pasta_destino:
        print("Seleção de pasta de destino cancelada.")
        return

    for raiz, diretorios, arquivos in os.walk(pasta_raiz):
        for arquivo in arquivos:
            if 'rxlev' in arquivo:
                caminho_arquivo = os.path.join(raiz, arquivo)
                dados_extraidos = extrair_dados_kml(caminho_arquivo)

                nome_arquivo_tratado = f"{os.path.splitext(arquivo)[0]}_tratado.txt"
                caminho_arquivo_tratado = os.path.join(
                    pasta_destino, nome_arquivo_tratado)

                with open(caminho_arquivo_tratado, 'w', newline='') as arquivo_tratado:
                    escritor = csv.writer(arquivo_tratado, delimiter='\t')
                    escritor.writerow(["Latitude", "Longitude", "CGI", "NODE", "CELLID", "PC", "TECHNOLOGY",
                                       "RSRP", "RSRQ", "DL_BITRATE", "UL_BITRATE", "SNR", "TIME", "BAND", "BANDWITH", "HEIGHT"])
                    escritor.writerows(dados_extraidos)

                print(
                    f"Dados gravados com sucesso no arquivo tratado: {caminho_arquivo_tratado}")


# Chamar a função para percorrer a pasta raiz e suas subpastas
percorrer_pasta()
