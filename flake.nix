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
          pyUTMEnv = pkgs.python3.withPackages (ps: with ps; [
            pkgs.pythonPackages.pyUTM

            # Other useful Python packages
            tabulate

            # Dev tools
            jedi
            flake8
            pylint
          ]);
        };

        defaultPackage = packages.pyUTMEnv;
        devShell = packages.pyUTMEnv.env;
      });
}
