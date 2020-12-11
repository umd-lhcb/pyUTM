final: prev:

{
  pythonPackagesOverrides = (prev.pythonPackagesOverride or [ ]) ++ [
    (self: super: {
      pyUTM = self.callPackage ./default.nix { };
    })
  ];

  # Remove when https://github.com/NixOS/nixpkgs/pull/91850 is fixed.
  python3 =
    let
      composeOverlays = prev.lib.foldl' prev.lib.composeExtensions (self: super: { });
      self = prev.python3.override {
        inherit self;
        packageOverrides = composeOverlays final.pythonPackagesOverrides;
      };
    in
    self;
}
