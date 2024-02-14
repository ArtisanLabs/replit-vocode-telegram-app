{pkgs}: {
  deps = [
    pkgs.neovim
    pkgs.libxcrypt
    pkgs.ffmpeg_6-full.bin
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
