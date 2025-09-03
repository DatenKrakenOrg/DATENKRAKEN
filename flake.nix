{
  description = "Datenkraken";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, treefmt-nix }:
    let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
      };
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs;[
          uv
          pre-commit
          platformio
          clang_19
          gcc
          python3
          python3Packages.numpy
          python3Packages.pandas
          pkgs.python313Packages.weasyprint
          pkgs.gobject-introspection
          pkgs.cairo
          pkgs.pango
          pkgs.gtk3
          pkgs.glib
        ];

        shellHook = ''
          echo "Started DEVSHELL";
        '';
      };
      formatter.x86_64-linux = treefmt-nix.lib.mkWrapper
        nixpkgs.legacyPackages.x86_64-linux
        {
          projectRootFile = "flake.nix";
          programs.nixpkgs-fmt.enable = true;
        };
    };
}
