[![Run on Repl.it](https://repl.it/badge/github/ArtisanLabs/replit-vocode-telegram-app)](https://repl.it/github/ArtisanLabs/replit-vocode-telegram-app)

[![Telegram](https://img.shields.io/badge/Telegram-CoquiTributeBot-blue?style=flat-square&logo=telegram)](https://t.me/CoquiTributeBot)


<p align="center">
  <img src="assets/images/CoquiTributeBot.jpg" width="200" height="200">
</p>

## A Note on Open Source

This project was initially built with the help of [Coqui](https://github.com/coqui-ai), an open-source project that we deeply admire and appreciate. Unfortunately, Coqui has ceased operations, reminding us of the importance of supporting open-source initiatives. 

Open-source projects, such as Coqui, provide immense value to the tech community by driving innovation and offering resources that are accessible to everyone. Without our support, we might all end up using Microsoft, like this project! (Just kidding 😅)

So, let's remember to contribute to and support our favorite open-source projects. We can do this by using the SAS services they create, which will help these projects become self-sustaining. They need us as much as we need them. 💚


# Vocode Telegram bot + Azure TTS on Replit

This project demonstrates how to use Microsoft Azure's Text-to-Speech (TTS) service with the Vocode library on Replit. It's a rewrite of a previous demo that used the now-closed Coqui service.

## Getting Started

To get started with this project, you need to have a [Replit](https://replit.com/signup).
Additionally, you will need to obtain the following API keys:

- [Microsoft Azure Speech Key](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=linux%252Cterminal)
- [Deepgram API Key](https://developers.deepgram.com/docs/make-your-first-api-request)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart?context=python)
- [Telegram Bot Key](https://core.telegram.org/bots#how-do-i-create-a-bot)

## ADD scret in replit
To add secrets to your Replit project, follow these steps:
1. Open your Replit project.
2. Navigate to the 'Secrets' tab on the left sidebar, which looks like a lock icon.
3. In the Replit interface, locate and click the 'Secrets' tab, represented by a lock icon.
4. Instead of manually entering secrets, click the 'Edit as JSON' button.
5. In the JSON editor, you can add all your secrets in the following format:
6. After adding your secrets, click the 'Save' button to store them securely.

```json
{
  "AZURE_SPEECH_REGION": "",
  "DEEPGRAM_API_KEY": "",
  "TELEGRAM_BOT_KEY": "",
  "OPENAI_API_KEY": "",
  "AZURE_SPEECH_KEY": ""
}
```

## Replit/Nix and Microsoft Azure's speech-SDK

The main challenge with this project is that Microsoft Azure's speech-SDK does not support OpenSSL 3.0. To make Azure Speech-SDK work, you must do several things that are not trivial in Replit. 

You need to add the following dependencies in your `replit.nix` file:

```nix:replit.nix
{pkgs}: {
  deps = [
    pkgs.neovim
    pkgs.libxcrypt
    pkgs.ffmpeg-full
    pkgs.libuuid
    pkgs.openssl_1_1
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libuuid
      pkgs.alsa-lib
      pkgs.openssl_1_1
    ];
    NIXPKGS_ALLOW_INSECURE="1";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libuuid
    ];
  };
}
```

And add the following to your `.config/nixpkgs/config.nix` file:

```nix:.config/nixpkgs/config.nix
{
  permittedInsecurePackages = [
    "openssl-1.1.1u"
  ];
}
```

```nix:./configuration.nix
{
    nixpkgs.config.permittedInsecurePackages = [
    "openssl-1.1.1u"
    ];
}
```

## Running the Project


The main script for this project is `main.py`. This script uses the Vocode library to create a voice-to-voice chatbot that uses Microsoft Azure's TTS service. 

To run the project, simply execute the `main.py` script.

### pydantic v2 support

In the Replit bash, manually install Vocode from Git:

```bash
pip install git+https://github.com/ArtisanLabs/vocode-python.git@486-support-for-pydantic-v2-v1-compatible
```

## Built With

- [Vocode](https://docs.vocode.dev/open-source/python-quickstart) - The library used to create the voice-to-voice chatbot
- [Microsoft Azure](https://azure.microsoft.com/) - The cloud service provider used for TTS
- [Replit](https://replit.com/) - The online IDE used
- [Deepgram](https://www.deepgram.com/) - The automatic speech recognition service used
- [OpenAI](https://openai.com/) - The artificial intelligence research lab used for generating responses

## Acknowledgments

- This project pays tribute to the exceptional work accomplished by [@_josh_meyer_](https://github.com/JRMeyer) and [@erogol](https://github.com/erogol) at [Coqui](https://github.com/coqui-ai), which has unfortunately ceased operations.
- Special thanks to [@Kian](https://github.com/Kian1354) for his support and encouragement to publish this demo.
- Video of the previous demo can be found [here](https://twitter.com/vocodehq/status/1673402815576969217)

![CoquiTributeBot Banner](assets/images/arpagon__Design_a_banner_for_The_CoquiTributeBot_a_frog_in_the__f1d14fa2-911e-4f76-b7df-9e48cf4cce30_resized.png)