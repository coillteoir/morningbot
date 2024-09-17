{
  description = "morningbot";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell rec {
      buildInputs = [
        (pkgs.python3.withPackages
          (python-pkgs: [
          python-pkgs.discordpy 
          python-pkgs.requests 
          python-pkgs.pytz
          ]))
        pkgs.black
        pkgs.vscodium
        pkgs.mypy
        pkgs.pylint
      ];
    };
  };
}
