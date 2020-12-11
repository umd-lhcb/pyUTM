final: prev:
let
  pythonOverrides = {
    packageOverrides = self: super: {
      pyUTM = self.callPackage ./default.nix { };
    };
  };
in
{
  python3 = prev.python3.override pythonOverrides;
}
