{ stdenv
, buildPythonPackage
, openpyxl
, pyparsing
, pyyaml
, multipledispatch
}:

buildPythonPackage rec {
  pname = "pyUTM";
  version = "0.2.0";

  src = builtins.path { path = ./..; name = pname; };

  propagatedBuildInputs = [
    openpyxl
    pyparsing
    pyyaml
    multipledispatch
  ];

  doCheck = false;
}
