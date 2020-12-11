{
  description = "Python library for Pcad netlist parsing and mapping generation";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    {
      overlay = import ./nix/overlay.nix;
    }
    //
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      rec {
        packages = {
          pyUTM = pkgs.python3.withPackages (ps: with ps; [ pyUTM ]);
        };

        defaultPackage = packages.pyUTM;
        devShell = packages.pyUTM.env;
      });
}
