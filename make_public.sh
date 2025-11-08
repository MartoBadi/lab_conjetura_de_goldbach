# Lista todos los repos privados de tu cuenta (hasta 1000, ajusta si tienes más)
gh repo list MartoBadi --visibility private -L 1000 | cut -f1 > private_repos.txt

# Cambia cada uno a público
while read repo; do
  echo "Cambiando $repo a público..."
  gh repo edit "$repo" --visibility public --accept-visibility-change-consequences
done < private_repos.txt

# Limpia el archivo temporal
rm private_repos.txt