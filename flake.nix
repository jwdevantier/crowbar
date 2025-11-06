{
  description = "python development flake";

  inputs = { nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05"; };

  outputs = { self, nixpkgs }:
    let
      allSystems = [
        "x86_64-linux" # AMD/Intel Linux
        "x86_64-darwin" # AMD/Intel macOS
        "aarch64-linux" # ARM Linux
        "aarch64-darwin" # ARM macOS
      ];

      forAllSystems = fn:
        nixpkgs.lib.genAttrs allSystems
        (system: fn { pkgs = import nixpkgs { inherit system; }; });
    in {
      # used when calling `nix fmt <path/to/flake.nix>`
      formatter = forAllSystems ({ pkgs }: pkgs.nixfmt);

      # nix develop <flake-ref>#<name>
      # --
      # $ nix develop <flake-ref>#blue
      # $ nix develop <flake-ref>#yellow
      devShells = forAllSystems ({ pkgs }: {
        default = pkgs.mkShell {
          name = "py3";
          nativeBuildInputs = with pkgs;
            [
              pyright
              poetry
              ];
          buildInputs = with pkgs; [
            # each release should support non-EOL'ed versions of Python, see
            # https://devguide.python.org/versions/
            python313
            python312
            python311
            python310
            stdenv.cc.cc.lib
            gcc-unwrapped.lib
          ];
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.gcc-unwrapped.lib
          ];
          shellHook = ''
            dev_root=""
            current_dir="$PWD"
            while [[ "$current_dir" != "/" ]]; do
              if [[ -f "$current_dir/.python-dev-root" ]]; then
                dev_root="$current_dir"
                break
              fi
              current_dir="$(dirname "$current_dir")"
            done

            if [[ -z "$dev_root" ]]; then
              echo "could not find '.python-dev-root' in current directory or any of the parent directories"
              echo ""
              echo "Please navigate to your python project and try again"
              exit 1
            fi

            export POETRY_VIRTUALENVS_IN_PROJECT=true
            cd "$dev_root"

            if [ -f "pyproject.toml" ]; then
              poetry sync
              echo "entering"
              source .venv/bin/activate
            else
              echo "No pyproject.toml found, to initialize:"
              echo "poetry init"
              echo "poetry add <package>"
            fi
          '';
        };
      });
    };
}
