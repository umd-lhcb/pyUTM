final: prev:
let
  pythonOverrides = {
    packageOverrides = self: super: {
      pyUTM = self.callPackage ./default.nix { };
    };
  };
in
rec {
  python3 = prev.python3.override pythonOverrides;
  pythonPackages = python3.pkgs;
}
