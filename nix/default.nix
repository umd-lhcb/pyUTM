{ stdenv
, buildPythonPackage
, openpyxl
, pyparsing
, pyyaml
, multipledispatch
}:

buildPythonPackage rec {
  pname = "pyUTM";
  version = "0.1";

  src = builtins.path { path = ./..; name = "pyUTM"; };

  propagatedBuildInputs = [
    openpyxl
    pyparsing
    pyyaml
    multipledispatch
  ];

  doCheck = false;
}
