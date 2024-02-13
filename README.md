[![Run on Repl.it](https://repl.it/badge/github/ArtisanLabs/replit-vocode-telegram-app)](https://repl.it/github/ArtisanLabs/replit-vocode-telegram-app)


# Vocode Telegram bot + Azure TTS on Replit

This project demonstrates how to use Microsoft Azure's Text-to-Speech (TTS) service with the Vocode library on Replit. It's a rewrite of a previous demo that used the now-closed Coqui service.

## Getting Started

To get started with this project, you need to have a [Replit](https://replit.com/signup).
Additionally, you will need to obtain the following API keys:

- [Microsoft Azure Speech Key](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-speech-to-text?tabs=linux%252Cterminal)
- [Deepgram API Key](https://developers.deepgram.com/docs/make-your-first-api-request)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart?context=python)
- [Telegram Bot Key](https://core.telegram.org/bots#how-do-i-create-a-bot)

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

## Running the Project

The main script for this project is `main.py`. This script uses the Vocode library to create a voice-to-voice chatbot that uses Microsoft Azure's TTS service. 

To run the project, simply execute the `main.py` script.

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
