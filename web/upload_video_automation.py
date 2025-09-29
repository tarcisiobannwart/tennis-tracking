#!/usr/bin/env python3
"""
Script para automatizar o upload de vídeo usando Playwright
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def upload_video():
    # Configurações
    url = "http://localhost:3000/live"
    video_path = "/Users/tarcisiobannwart/DEVELOP/projetos/tennis-tracking/data/samples/input/video_input2.mp4"

    # Verificar se o arquivo existe
    if not os.path.exists(video_path):
        print(f"❌ Arquivo de vídeo não encontrado: {video_path}")
        return False

    print(f"📁 Arquivo de vídeo encontrado: {video_path}")
    print(f"📄 Tamanho do arquivo: {os.path.getsize(video_path) / (1024*1024):.2f} MB")

    async with async_playwright() as p:
        # Lançar o browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print(f"🌐 Navegando para {url}...")
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path="screenshot_1_page_loaded.png")
            print("📸 Screenshot 1: Página carregada")

            # Aguardar a página carregar completamente
            await page.wait_for_timeout(2000)

            # Procurar especificamente pelo botão "Upload Video" na área principal
            upload_button = None

            # Primeiro, tentar encontrar o botão Upload Video na área central
            try:
                # Procurar por todos os botões com "Upload Video"
                buttons = await page.locator('button:has-text("Upload Video")').all()
                print(f"📊 Encontrados {len(buttons)} botões 'Upload Video'")

                if len(buttons) > 1:
                    # Se há múltiplos botões, pegar o segundo (assumindo que o primeiro está no header)
                    upload_button = buttons[1]
                    print("✅ Segundo botão 'Upload Video' encontrado (área principal)")
                elif len(buttons) == 1:
                    upload_button = buttons[0]
                    print("✅ Botão 'Upload Video' único encontrado")
            except Exception as e:
                print(f"❌ Erro ao procurar botões Upload Video: {e}")
                pass

            # Se ainda não encontrou, tentar seletores alternativos
            if not upload_button:
                upload_selectors = [
                    '[data-testid="upload-button"]',
                    'button[class*="upload"]',
                    '.upload-button',
                    '#upload-button'
                ]

                for selector in upload_selectors:
                    try:
                        upload_button = await page.wait_for_selector(selector, timeout=3000)
                        if upload_button:
                            print(f"✅ Botão de upload encontrado com seletor: {selector}")
                            break
                    except:
                        continue

            if not upload_button:
                print("❌ Botão de upload não encontrado!")
                await page.screenshot(path="screenshot_error_no_button.png")
                return False

            # Capturar screenshot antes de clicar
            await page.screenshot(path="screenshot_2_before_click.png")
            print("📸 Screenshot 2: Antes de clicar no botão")

            # Clicar no botão de upload
            print("🖱️ Clicando no botão de upload...")
            if hasattr(upload_button, 'click'):
                await upload_button.click()
            else:
                # Se for um locator, usar o método click do locator
                await upload_button.click()

            # Aguardar modal ou input de arquivo aparecer
            await page.wait_for_timeout(1000)

            # Capturar screenshot após clicar
            await page.screenshot(path="screenshot_3_after_click.png")
            print("📸 Screenshot 3: Após clicar no botão")

            # Procurar diretamente por inputs de arquivo (incluindo ocultos)
            file_input = None

            # Procurar por todos os inputs de arquivo, incluindo ocultos
            file_selectors = [
                'input[type="file"]',
                '[data-testid="file-input"]',
                '.file-input',
                'input[accept*="video"]',
                'input[accept*=".mp4"]'
            ]

            print("🔍 Procurando por inputs de arquivo (incluindo ocultos)...")

            for selector in file_selectors:
                try:
                    # Usar locator.all() para encontrar todos os inputs, incluindo ocultos
                    inputs = await page.locator(selector).all()
                    if inputs:
                        file_input = inputs[0]  # Pegar o primeiro encontrado
                        print(f"✅ Input de arquivo encontrado com seletor: {selector}")
                        break
                except:
                    continue

            # Se não encontrou, tentar uma busca mais ampla
            if not file_input:
                print("🔍 Fazendo busca ampla por inputs de arquivo...")
                try:
                    # Procurar todos os inputs de arquivo na página
                    all_file_inputs = await page.locator('input[type="file"]').all()
                    if all_file_inputs:
                        file_input = all_file_inputs[-1]  # Pegar o último (provavelmente o do modal)
                        print(f"✅ Encontrado input de arquivo (total: {len(all_file_inputs)})")
                    else:
                        print("❌ Nenhum input de arquivo encontrado na página")
                except Exception as e:
                    print(f"❌ Erro ao procurar inputs: {e}")

            if not file_input:
                print("❌ Input de arquivo não encontrado!")
                await page.screenshot(path="screenshot_error_no_input.png")
                return False

            # Fazer upload do arquivo
            print(f"📤 Fazendo upload do arquivo: {video_path}")
            await file_input.set_input_files(video_path)

            # Aguardar um pouco para o upload começar
            await page.wait_for_timeout(2000)

            # Capturar screenshot durante o upload
            await page.screenshot(path="screenshot_4_upload_started.png")
            print("📸 Screenshot 4: Upload iniciado")

            # Aguardar indicadores de upload (progressbar, spinner, etc.)
            upload_indicators = [
                '.progress',
                '.loading',
                '.spinner',
                '[data-testid="upload-progress"]',
                '.upload-progress'
            ]

            upload_in_progress = False
            for selector in upload_indicators:
                try:
                    indicator = await page.wait_for_selector(selector, timeout=3000)
                    if indicator:
                        print(f"✅ Indicador de upload encontrado: {selector}")
                        upload_in_progress = True
                        break
                except:
                    continue

            if upload_in_progress:
                print("⏳ Aguardando conclusão do upload...")
                # Aguardar até que o indicador de progresso desapareça
                for selector in upload_indicators:
                    try:
                        await page.wait_for_selector(selector, state="detached", timeout=60000)
                        print(f"✅ Upload concluído (indicador {selector} removido)")
                        break
                    except:
                        continue
            else:
                print("⏳ Aguardando 10 segundos para conclusão do upload...")
                await page.wait_for_timeout(10000)

            # Capturar screenshot final
            await page.screenshot(path="screenshot_5_upload_complete.png")
            print("📸 Screenshot 5: Upload concluído")

            # Procurar por mensagens de sucesso
            success_messages = [
                ':has-text("sucesso")',
                ':has-text("success")',
                ':has-text("completed")',
                ':has-text("concluído")',
                '.success',
                '.alert-success'
            ]

            for selector in success_messages:
                try:
                    success_element = await page.wait_for_selector(selector, timeout=3000)
                    if success_element:
                        text = await success_element.text_content()
                        print(f"✅ Mensagem de sucesso encontrada: {text}")
                        break
                except:
                    continue

            print("✅ Processo de upload automatizado concluído com sucesso!")
            return True

        except Exception as e:
            print(f"❌ Erro durante a automação: {e}")
            await page.screenshot(path="screenshot_error.png")
            return False

        finally:
            await browser.close()

async def main():
    print("🤖 Iniciando automação de upload de vídeo...")
    success = await upload_video()

    if success:
        print("\n✅ Automação concluída com sucesso!")
        print("📸 Screenshots capturadas:")
        screenshots = [
            "screenshot_1_page_loaded.png",
            "screenshot_2_before_click.png",
            "screenshot_3_after_click.png",
            "screenshot_4_upload_started.png",
            "screenshot_5_upload_complete.png"
        ]
        for screenshot in screenshots:
            if os.path.exists(screenshot):
                print(f"  - {screenshot}")
    else:
        print("\n❌ Automação falhou. Verifique os screenshots de erro.")

if __name__ == "__main__":
    asyncio.run(main())