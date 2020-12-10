{
  description = "Python library for Pcad netlist parsing and mapping generation";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs { overlays = [ (import ./nix/overlay.nix) ]; };
    in
    rec {
      packages = {
        pyUTMEnv = pkgs.legacyPackages.${system}.python3.withPackages (ps: with ps; [ pyUTM ]);
      };

      defaultPackage = packages.pyUTMEnv;
      devShell = packages.pyUTMEnv.env;
    });
}
