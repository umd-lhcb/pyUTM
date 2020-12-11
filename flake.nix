{
  description = "Python library for Pcad netlist parsing and mapping generation";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (import nixpkgs {
          inherit system;
          overlays = [ (import ./nix/overlay.nix) ];
        });
      in
      rec {
        defaultPackage = pkgs.python3.pkgs.pyUTM;
        devShell = (pkgs.python3.withPackages (ps: with ps; [ pyUTM ])).env;
      });
}
