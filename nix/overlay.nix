self: super:
let
  pythonOverride = {
    packageOverrides = self: super: {
      pyUTM = self.callPackage ./default.nix { };
    };
  };
in
{
  python3 = super.python3.override pythonOverride;
}
